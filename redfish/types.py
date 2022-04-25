# coding=utf-8
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
from builtins import object

import pprint
from urllib.parse import urljoin
import requests
import simplejson
import tortilla
import ssl
from . import config
from . import mapping
from . import exception

standard_library.install_aliases()


# Global variable


class Base(object):
    '''Abstract class to manage types (Chassis, Servers etc...).'''
    def __init__(self, url, connection_parameters):
        '''Class constructor'''
        global TORTILLADEBUG
        self.connection_parameters = connection_parameters  # Uggly hack
        self.url = url
        self.api_url = tortilla.wrap(url, debug=config.TORTILLADEBUG)

        config.logger.debug(
            "------------------------------------------------------------")
        config.logger.debug("Url: %s" % url)
        config.logger.debug("Header: %s" % connection_parameters.headers)
        config.logger.debug(
            "------------------------------------------------------------")

        try:
            self.data = self.api_url.get(
                verify=connection_parameters.verify_cert,
                headers=connection_parameters.headers)
        except (requests.ConnectionError, ssl.SSLError) as e:
            # Log and transmit the exception.
            config.logger.info('Raise a RedfishException to upper level')
            msg = 'Connection error : {}\n'.format(e)
            raise exception.ConnectionFailureException(msg)
        except simplejson.scanner.JSONDecodeError as e:
            # Log and transmit the exception.
            config.logger.info('Raise a RedfishException to upper level')
            msg = \
                'Ivalid content : Content does not appear to be a valid ' + \
                'Redfish json\n'
            raise exception.InvalidRedfishContentException(msg)
        config.logger.debug(pprint.PrettyPrinter(indent=4).pformat(self.data))

    def get_link_url(self, link_type, data_subset=None):
        '''Need to be explained.

        :param parameter_name: name of the parameter
        :returns:  string -- parameter value
        '''
        if not data_subset:
            data = self.data
        else:
            data = data_subset

        self.links = []

        # Manage standard < 1.0
        if float(mapping.redfish_version) < 1.00:
            links = getattr(data, mapping.redfish_mapper.map_links())
            if link_type in links:
                return urljoin(
                    self.url,
                    links[link_type][mapping.redfish_mapper.map_links_ref()])
            raise AttributeError
        else:
            links = getattr(data, link_type)
            link = getattr(links, mapping.redfish_mapper.map_links_ref())
            return urljoin(self.url, link)

    @property
    def url(self):
        return self.__url

    @url.setter
    def url(self, url):
        self.__url = url

    def get_parameter(self, parameter_name):
        '''Generic function to get a specific parameter

        :param parameter_name: name of the parameter
        :returns:  string -- parameter value

        '''
        try:
            return self.data[parameter_name]
        except:
            return 'Parameter does not exist'

    def get_parameters(self):
        '''Generic function to get all parameters

        :returns:  string -- parameter value

        '''
        try:
            return self.data
        except:
            return -1

    def set_parameter(self, parameter_name, value):
        '''Generic function to set a specific parameter

        :param parameter_name: name of the parameter
        :param value: value to set
        :returns:   string -- http response of PATCH request

        '''
        # Craft the request
        action = dict()
        action[parameter_name] = value
        config.logger.debug(action)

        # Perform the POST action
        config.logger.debug(self.api_url)
        response = self.api_url.patch(
            verify=self.connection_parameters.verify_cert,
            headers=self.connection_parameters.headers,
            data=action)
        return response

    def get_name(self):
        '''Get root name

        :returns:  string -- root name or "Not available"

        '''
        try:
            return self.data.Name
        except AttributeError:
            return "Not available"


class BaseCollection(Base):
    '''Abstract class to manage collection (Chassis, Servers etc...).'''
    def __init__(self, url, connection_parameters):
        super(BaseCollection, self).__init__(url, connection_parameters)

        self.links = []

        # linksmembers = self.data.Links.Members
        # linksmembers = self.data.links.Member
        if float(mapping.redfish_version) < 1.00:
            linksmembers = getattr(
                self.data, mapping.redfish_mapper.map_links())
            linksmembers = getattr(
                linksmembers, mapping.redfish_mapper.map_members())
        else:
            linksmembers = getattr(
                self.data, mapping.redfish_mapper.map_members())
        for link in linksmembers:
            # self.links.append(getattr(link,'@odata.id'))
            # self.links.append(getattr(link,'href'))
            self.links.append(urljoin(
                self.url, getattr(
                    link, mapping.redfish_mapper.map_links_ref())))

        config.logger.debug(self.links)


class Thermal(Base):
    '''Class to manage redfish Thermal data.'''

    # Currently doesn't support case such as:
    # /redfish/v1/Systems/1/SmartStorage/ArrayControllers/0/DiskDrives/1/
    # u'CurrentTemperatureCelsius': 45
    def get_temperatures(self):
        '''Get chassis sensors name and temperature

        :returns: chassis sensor and temperature
        :rtype: dict

        '''
        temperatures = {}

        try:
            for sensor in self.data.Temperatures:
                temperatures[sensor.Name] = sensor.ReadingCelsius
            return temperatures
        except AttributeError:
            return "Not available"

    def get_fans(self):
        '''Get chassis fan name and rpm

        :returns: chassis fan and rpm
        :rtype: dict

        '''
        fans = {}

        try:
            for fan in self.data.Fans:
                # New interface
                fans[fan.Name] = str(fan.Reading) + ' ' + fan.ReadingUnits
            return fans
        except AttributeError:
            try:
                # Old interface
                for fan in self.data.Fans:
                    fans[fan.FanName] = fan.ReadingRPM

                return fans

            except AttributeError:
                return "Not available"


class Power(Base):
    '''Class to manage redfish Power data.'''

    def get_power(self):
        '''Get power supply informartion

        :returns: power supply and Voltage
        :rtype: dict

        '''
        pc = {}

        # config.logger.debug("PowerControl parsed")
        # config.logger.debug(self.data)
        try:
            for p in self.data.PowerControl:
                pc[p.MemberId] = str(p.PowerConsumedWatts) + ' Watts'
            return pc
        except AttributeError:
            return "Not available"


class Device(Base):
    '''Abstract class to add common methods between devices
    (Chassis, Servers, System).
    '''

    def __init__(self, url, connection_parameters):
        '''Class constructor'''
        super(Device, self).__init__(url, connection_parameters)

        try:
            url2 = self.get_link_url('Thermal')
            self.thermal = Thermal(url2, connection_parameters)
        except AttributeError:
            self.thermal = Thermal(url, connection_parameters)

        try:
            url2 = self.get_link_url('Power')
            self.power = Power(url2, connection_parameters)
        except AttributeError:
            self.power = Power(url, connection_parameters)

    def get_uuid(self):
        '''Get device uuid

        :returns: device uuid or "Not available"
        :rtype: string

        '''
        try:
            return self.data.UUID
        except AttributeError:
            return "Not available"

    def get_status(self):
        '''Get device status

        :returns: device status or "Not available"
        :rtype: dict

        '''
        try:
            return self.data.Status
        except AttributeError:
            return "Not available"

    def get_model(self):
        '''Get device model

        :returns: device model or "Not available"
        :rtype: string

        '''
        try:
            return self.data.Model
        except AttributeError:
            return "Not available"

    def get_manufacturer(self):
        '''Get device manufacturer

        :returns: device manufacturer or "Not available"
        :rtype: string

        '''
        try:
            return self.data.Manufacturer
        except AttributeError:
            return "Not available"

    def get_serial_number(self):
        '''Get serial number of the device.

        :returns:  serial number or "Not available"
        :rtype: string

        '''
        try:
            return self.data.SerialNumber
        except AttributeError:
            return "Not available"

    def get_asset_tag(self):
        '''Get asset tag of the device.

        :returns: asset tag or "Not available"
        :rtype: string

        '''
        try:
            return self.data.AssetTag
        except AttributeError:
            return "Not available"

    def get_sku(self):
        '''Get sku number of the device.

        :returns: sku number or "Not available"
        :rtype: string

        '''
        try:
            return self.data.SKU
        except AttributeError:
            return "Not available"

    def get_part_number(self):
        '''Get part number of the device.

        :returns: part number or "Not available"
        :rtype: string

        '''
        try:
            return self.data.PartNumber
        except AttributeError:
            return "Not available"

    def get_name(self):
        '''Get name of the device.

        :returns: name or "Not available"
        :rtype: string

        '''
        try:
            return self.data.Name
        except AttributeError:
            try:
                return self.data.ProductName
            except AttributeError:
                return "Not available"

    def get_description(self):
        '''Get description of the device.

        :returns: device description or "Not available"
        :rtype: string

        '''
        try:
            return self.data.Description
        except AttributeError:
            return "Not available"

    def get_powerstate(self):
        '''Get power status of the device.

        :returns: device power state or "Not available"
        :rtype: string

        '''
        try:
            return self.data.PowerState
        except AttributeError:
            return "Not available"

    def get_fw_version(self):
        '''Get firmware version of the device.

        :returns: firmware version or "Not available"
        :rtype: string

        '''
        try:
            return self.data.FirmwareVersion.Current.VersionString
        except AttributeError:
            try:
                return self.data.Firmware.Current.VersionString
            except AttributeError:
                # For some NICs
                try:
                    return self.data.FirmwareVersion
                except AttributeError:
                    try:
                        return self.data.Firmware
                    except AttributeError:
                        return "Not available"
