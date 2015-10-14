# coding=utf-8

import pprint
from urlparse import urljoin
import requests
import tortilla
import config
import mapping
import re

# Global variable


class Base(object):
    """Abstract class to manage types (Chassis, Servers etc...)."""

    def __init__(self, url, connection_parameters):
        """Class constructor"""
        global TORTILLADEBUG
        self.connection_parameters = connection_parameters # Uggly hack to check
        self.url = url
        self.api_url = tortilla.wrap(url, debug=config.TORTILLADEBUG)

        try:
            if connection_parameters.auth_token == None:
                self.data = self.api_url.get(verify=connection_parameters.verify_cert)
            else:
                self.data = self.api_url.get(verify=connection_parameters.verify_cert,
                                             headers={'x-auth-token': connection_parameters.auth_token}
                                             )
        except requests.ConnectionError as e:
            print e
            # Log and transmit the exception.
            config.logger.error("Connection error : %s", e)
            raise e
        print self.data

    def get_link_url(self, link_type):
        """Need to be explained.

        :param redfish_logfile: redfish log
        :type str
        :returns:  True

        """
        self.links=[]
        
        # Manage standard < 1.0
        if float(mapping.redfish_version) < 1.00:
            links = getattr(self.data, mapping.redfish_mapper.map_links())
            if link_type in links:
                return  urljoin(self.url, links[link_type][mapping.redfish_mapper.map_links_ref()])
        else:
            links = getattr(self.data, link_type)
            link = getattr(links, mapping.redfish_mapper.map_links_ref())
            return  urljoin(self.url, link)
        
    @property
    def url(self):
        return self.__url

    @url.setter
    def url(self, url):
        self.__url = url


class BaseCollection(Base):
    """Abstract class to manage collection (Chassis, Servers etc...)."""

    def __init__(self, url, connection_parameters):
        super(BaseCollection, self).__init__(url, connection_parameters)

        self.links=[]
        

        #linksmembers = self.data.Links.Members
        #linksmembers = self.data.links.Member
        if float(mapping.redfish_version) < 1.00:
            linksmembers = getattr(self.data, mapping.redfish_mapper.map_links())
            linksmembers = getattr(linksmembers, mapping.redfish_mapper.map_members())
        else:
            linksmembers = getattr(self.data, mapping.redfish_mapper.map_members())
        for link in linksmembers:
            #self.links.append(getattr(link,"@odata.id"))
            #self.links.append(getattr(link,"href"))
            self.links.append(urljoin(self.url, getattr(link, mapping.redfish_mapper.map_links_ref())))


        print self.links


class Root(Base):
    """Class to manage redfish Root data."""

    def get_api_version(self):
        """Return api version.

        :returns:  string -- version
        :raises: AttributeError

        """
        try:
            version = self.data.RedfishVersion
        except AttributeError:
            version = self.data.ServiceVersion
        
        version = version.replace('.', '')
        version = version[0] + '.' + version[1:]
        return(version)

    def get_api_UUID(self):
        """Return UUID version.

        :returns:  string -- UUID

        """
        return self.data.UUID


    def get_api_link_to_server(self):
        """Return api link to server.

        :returns:  string -- path

        """
        return getattr(self.root.Links.Systems, "@odata.id")


class SessionService(Base):
    """Class to manage redfish SessionService data."""
    pass


class Managers(Base):
    """Class to manage redfish Managers."""
    def __init__(self, url, connection_parameters):
        super(Managers, self).__init__(url, connection_parameters)
        
        try:
            
#             self.ethernet_interfaces_collection = EthernetInterfacesCollection(
#                                                         self.get_link_url("EthernetInterfaces"),
#                                                         connection_parameters
#                                                         )

            # Works on proliant, need to treat 095 vs 0.96 differences
            self.ethernet_interfaces_collection = EthernetInterfacesCollection(
                                                        self.get_link_url("EthernetNICs"),
                                                        connection_parameters
                                                        )
        except:
            pass


class ManagersCollection(BaseCollection):
    """Class to manage redfish ManagersCollection data."""
    def __init__(self, url, connection_parameters):
        """Class constructor"""
        super(ManagersCollection, self).__init__(url, connection_parameters)
        self.managers_list = []
        for link in self.links:
            self.managers_list.append(Managers(link, connection_parameters))

class Systems(Base):
    """Class to manage redfish Systems data."""
    # TODO : Need to discuss with Bruno the required method.
    #        Also to check with the ironic driver requirement.
    def __init__(self, url, connection_parameters):
        """Class constructor"""
        super(Systems, self).__init__(url, connection_parameters)
        self.bios = Bios(url+"Bios/Settings", connection_parameters)
        
    def reset_system(self):
        """Force reset of the system.

        :returns:  string -- http response of POST request
        
        """
        # Craft the request
        action = dict()
        action['Action'] = 'Reset'
        action['ResetType'] = 'ForceRestart'

        #Debug the url and perform the POST action
        #print self.api_url
        response = self.api_url.post(verify=self.connection_parameters.verify_cert,
                                     headers={'x-auth-token': self.connection_parameters.auth_token},
                                     data=action
                                    )
        #TODO : treat response.
        return response
    
    def get_bios_version(self):
        """Get bios version of the system.

        :returns:  string -- bios version
        
        """
        try:
            # Returned by proliant
            return self.data.Bios.Current.VersionString
        except:
            # Returned by mockup.
            # Hopefully this kind of discrepencies will be fixed with Redfish 1.0 (August)
            return self.data.BiosVersion

    def get_serial_number(self):
        """Get serial number of the system.

        :returns:  string -- serial number
        
        """
        try:
            # Returned by proliant
            return self.data.SerialNumber
        except:
            # Returned by mockup.
            # Hopefully this kind of discrepencies will be fixed with Redfish 1.0 (August)
            return ""
        
    def get_power(self):
        """Get power status of the system.

        :returns:  string -- power status or NULL if there is an issue
        
        """
        try:
            return self.data.Power
        except:
            return ""
        
    def get_parameter(self, parameter_name):
        """Generic function to get any system parameter

        :param parameter_name: name of the parameter
        :returns:  string -- parameter value
        
        """
        try:
            return self.data[parameter_name]
        except:
            return "Parameter does not exist"
        
    def set_parameter(self, parameter_name, value):
        """Generic function to set any system parameter

        :param parameter_name: name of the parameter
        :param value: value to set
        :returns:   string -- http response of PATCH request
        
        """
        # Craft the request
        action = dict()
        action[parameter_name] = value
        print(action)

        # Perform the POST action
        print self.api_url
        response = self.api_url.patch(verify=self.connection_parameters.verify_cert,
                                     headers={'x-auth-token': self.connection_parameters.auth_token},
                                     data=action
                                     )   
        return response  
        
    def set_parameter_json(self, value):
        """Generic function to set any system parameter using json structure

        :param value: json structure with value to update
        :returns:   string -- http response of PATCH request
        
        """
        # perform the POST action
        print self.api_url.url()
                
        response = requests.patch(self.api_url.url(),
                                  verify=self.connection_parameters.verify_cert,
                                  headers={'x-auth-token': self.connection_parameters.auth_token, 'Content-type': 'application/json'},
                                  data=value)
        print(response.reason)

class SystemsCollection(BaseCollection):
    """Class to manage redfish ManagersCollection data."""
    def __init__(self, url, connection_parameters):
        super(SystemsCollection, self).__init__(url, connection_parameters)
        
        self.systems_list = []
        
        for link in self.links:
            self.systems_list.append(Systems(link, connection_parameters))

class Bios(Base):
    """Class to manage redfish Bios data."""
    def __init__(self, url, connection_parameters):
        super(Bios, self).__init__(url, connection_parameters)
        self.boot = Boot(re.findall(".+/Bios",url)[0]+"/Boot/Settings", connection_parameters)
        
    def get_parameters(self):
        """Generic function to get all system parameters

        :returns:  string -- parameter value
        
        """
        try:
            return self.data
        except:
            return -1
        
    def get_parameter(self, parameter_name):
        """Generic function to get any system parameter

        :param parameter_name: name of the parameter
        :returns:  string -- parameter value
        
        """
        try:
            return self.data[parameter_name]
        except:
            return "Parameter does not exist"
     
    def set_parameter(self, parameter_name, value):
        """Generic function to set any bios parameter

        :param parameter_name: name of the parameter
        :param value: value to set
        :returns:   string -- http response of PATCH request
        
        """
        # Craft the request
        action = dict()
        action[parameter_name] = value

        # perform the POST action
        print self.api_url
        response = self.api_url.patch(verify=self.connection_parameters.verify_cert,
                                     headers={'x-auth-token': self.connection_parameters.auth_token},
                                     data=action
                                    )
        return response
        
class Boot(Base):
    """Class to manage redfish Boot data."""
    def __init__(self, url, connection_parameters):
        super(Boot, self).__init__(url, connection_parameters)
        
    def get_parameters(self):
        """Generic function to get all system parameters

        :returns:  string -- parameter value
        
        """
        try:
            return self.data
        except:
            return -1        
    
    def get_parameter(self, parameter_name):
        """Generic function to get any system parameter

        :param parameter_name: name of the parameter
        :returns:  string -- parameter value
        
        """
        try:
            return self.data[parameter_name]
        except:
            return "Parameter does not exist"
     
    def set_parameter(self, parameter_name, value):
        """Generic function to set any bios parameter

        :param parameter_name: name of the parameter
        :param value: value to set
        :returns:   string -- http response of PATCH request
        
        """
        # Craft the request
        action = dict()
        action[parameter_name] = value

        # perform the POST action
        response = self.api_url.patch(verify=self.connection_parameters.verify_cert,
                                     headers={'x-auth-token': self.connection_parameters.auth_token},
                                     data=action
                                    )
        return response
    
class EthernetInterfacesCollection(BaseCollection):
    """Class to manage redfish EthernetInterfacesColkection data."""
    def __init__(self, url, connection_parameters):
        super(EthernetInterfacesCollection, self).__init__(url, connection_parameters)
        
        self.ethernet_interfaces_list = []
        
        # Url returned by the mock up is wrong /redfish/v1/Managers/EthernetInterfaces/1 returns a 404.
        # The correct one should be /redfish/v1/Managers/1/EthernetInterfaces/1
        # Check more than 1 hour for this bug.... grrr....
        for link in self.links:
            self.ethernet_interfaces_list.append(EthernetInterfaces(link, connection_parameters))

class EthernetInterfaces(Base):
    """Class to manage redfish EthernetInterfaces data."""
    pass