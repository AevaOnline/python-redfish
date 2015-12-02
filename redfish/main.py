# Copyright 2014 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.


"""
STARTING ASSUMPTIONS

On URIs:

The Redfish RESTful API is a "hypermedia API" by design.  This is to avoid
building in restrictive assumptions to the data model that will make it
difficult to adapt to future hardware implementations.  A hypermedia API avoids
these assumptions by making the data model discoverable via links between
resources.

A URI should be treated by the client as opaque, and thus should not be
attempted to be understood or deconstructed by the client.  Only specific top
level URIs (any URI in this sample code) may be assumed, and even these may be
absent based upon the implementation (e.g. there might be no /redfish/v1/Systems
collection on something that doesn't have compute nodes.)

The other URIs must be discovered dynamically by following href links.  This is
because the API will eventually be implemented on a system that breaks any
existing data model "shape" assumptions we may make now.  In particular,
clients should not make assumptions about the URIs for the resource members of
a collection.  For instance, the URI of a collection member will NOT always be
/redfish/v1/.../collection/1, or 2.  On systems with multiple compute nodes per
manager, a System collection member might be /redfish/v1/Systems/C1N1.

This sounds very complicated, but in reality (as these examples demonstrate),
if you are looking for specific items, the traversal logic isn't too
complicated.

On Resource Model Traversal:

Although the resources in the data model are linked together, because of cross
link references between resources, a client may not assume the resource model
is a tree.  It is a graph instead, so any crawl of the data model should keep
track of visited resources to avoid an infinite traversal loop.

A reference to another resource is any property called "href" no matter where
it occurs in a resource.

An external reference to a resource outside the data model is referred to by a
property called "extref".  Any resource referred to by extref should not be
assumed to follow the conventions of the API.

On Resource Versions:

Each resource has a "Type" property with a value of the format Tyepname.x.y.z
where
* x = major version - incrementing this is a breaking change to the schema y =
* minor version - incrementing this is a non-breaking additive change to the
* schema z = errata - non-breaking change

Because all resources are versioned and schema also have a version, it is
possible to design rules for "nearest" match (e.g. if you are interacting with
multiple services using a common batch of schema files).  The mechanism is not
prescribed, but a client should be prepared to encounter both older and newer
versions of resource types.

On HTTP POST to create:

WHen POSTing to create a resource (e.g. create an account or session) the
guarantee is that a successful response includes a "Location" HTTP header
indicating the resource URI of the newly created resource.  The POST may also
include a representation of the newly created object in a JSON response body
but may not.  Do not assume the response body, but test it.  It may also be an
ExtendedError object.

HTTP REDIRECT:

All clients must correctly handle HTTP redirect.  We (or Redfish) may
eventually need to use redirection as a way to alias portions of the data
model.

FUTURE:  Asynchronous tasks

In the future some operations may start asynchonous tasks.  In this case, the
client should recognized and handle HTTP 202 if needed and the 'Location'
header will point to a resource with task information and status.

JSON-SCHEMA:

The json-schema available at /redfish/v1/Schemas governs the content of the
resources, but keep in mind:
* not every property in the schema is implemented in every implementation.
* some properties are schemed to allow both null and anotehr type like string
* or integer.

Robust client code should check both the existence and type of interesting
properties and fail gracefully if expectations are not met.

GENERAL ADVICE:

Clients should always be prepared for:
* unimplemented properties (e.g. a property doesn't apply in a particular case)
* null values in some cases if the value of a property is not currently known
* due to system conditions HTTP status codes other than 200 OK.  Can your code
* handle an HTTP 500 Internal Server Error with no other info?  URIs are case
* insensitive HTTP header names are case insensitive JSON Properties and Enum
* values are case sensitive A client should be tolerant of any set of HTTP
* headers the service returns

"""

# coding=utf-8

import sys
import json
from urlparse import urlparse
import requests
import config
import types
import mapping
import exception

# Global variable definition
redfish_logfile = "/var/log/python-redfish/python-redfish.log"

# ===============================================================================
# TODO : create method to set logging level and TORTILLADEBUG.
# ===============================================================================


def set_log_file(logfile):
    global redfish_logfile
    redfish_logfile = logfile
    return True


""" Function to wrap RedfishConnection """


def connect(
        url,
        user,
        password,
        simulator=False,
        enforceSSL=True,
        verify_cert=True
    ):
    global redfish_logfile
    config.initialize_logger(redfish_logfile)
    return RedfishConnection(
        url,
        user,
        password,
        simulator=simulator,
        enforceSSL=enforceSSL,
        verify_cert=verify_cert
    )


class RedfishConnection(object):
    """Implements basic connection handling for Redfish APIs."""

    def __init__(self,
                 url,
                 user,
                 password,
                 simulator=False,
                 enforceSSL=True,
                 verify_cert=True
                ):
        """Initialize a connection to a Redfish service."""
        super(RedfishConnection, self).__init__()

        config.logger.info("Initialize python-redfish")

        self.connection_parameters = ConnectionParameters()
        self.connection_parameters.rooturl = url
        self.connection_parameters.user_name = user
        self.connection_parameters.password = password
        self.connection_parameters.enforceSSL = enforceSSL
        self.connection_parameters.verify_cert = verify_cert

        # Use DMTF mockup or not
        self.__simulator = simulator

        # Session attributes
        self.connection_parameters.auth_token = None
        self.connection_parameters.user_uri = None

        rooturl = urlparse(self.connection_parameters.rooturl)

        # Enforce ssl
        if self.connection_parameters.enforceSSL is True:
            config.logger.debug("Enforcing SSL")
            rooturl = rooturl._replace(scheme="https")
            self.connection_parameters.rooturl = rooturl.geturl()

        # Verify cert
        if self.connection_parameters.verify_cert is False:
            config.logger.info("Certificat is not checked, " +
                        "this is insecure and can allow" +
                        " a man in the middle attack")

        config.logger.debug("Root url : %s", self.connection_parameters.rooturl)
        self.Root = types.Root(self.connection_parameters.rooturl,
                         self.connection_parameters
                        )
        #self.api_url = tortilla.wrap(self.connection_parameters.rooturl,
        #                             debug=TORTILLADEBUG)
        #self.root = self.api_url.get(verify=self.connection_parameters.verify_cert)

        config.logger.info("API Version : %s", self.get_api_version())
        mapping.redfish_version = self.get_api_version()

        # Instanciate a global mapping object to handle Redfish version variation
        mapping.redfish_mapper = mapping.RedfishVersionMapping(self.get_api_version())

        # Now we need to login otherwise we are not allowed to extract data
        if self.__simulator is False:
            try:
                config.logger.info("Login to %s", rooturl.netloc)
                self.login()
                config.logger.info("Login successful")
            except "Error getting token":
                config.logger.error("Login fail, fail to get auth token")
                raise exception.AuthenticationFailureException("Fail to get an auth token.")



        # Struture change with mockup 1.0.0, there is no links
        # section anymore.
        # ===================================================================
        # TODO : Add a switch to allow the both structure
        # ===================================================================

        # Types
        self.SessionService = types.SessionService(
                                        self.Root.get_link_url(
                                            mapping.redfish_mapper.map_sessionservice()),
                                        self.connection_parameters
                                                   )

        self.Managers = types.ManagersCollection(self.Root.get_link_url("Managers"),
                                                 self.connection_parameters
                                                 )

        self.Systems = types.SystemsCollection(self.Root.get_link_url("Systems"),
                                                 self.connection_parameters
                                                 )

        #for system in self.Systems.systems_list:
            #config.logger.debug(system.data.links.ManagedBy)
#         self.Chassis

#         self.EventService
#         self.AccountService
#         self.Tasks




    # ========================================================================
    #     systemCollectionLink = getattr(self.root.Links.Systems,"@odata.id")
    #     self.systemCollection = self.apiUrl.redfish.v1.Systems.get()
    #
    #     print self.systemCollection.Name
    #
    # ======================================================================== 
    def get_api_version(self):
        """Return api version.

        :returns:  string -- version
        :raises: AttributeError

        """
        return (self.Root.get_api_version())

    def login(self):
        # Craft full url
        url = self.Root.get_link_url(
                                    mapping.redfish_mapper.map_sessionservice()
                                    )
        
        # Handle login with redfish 1.00, url must be : 
        # /rest/v1/SessionService/Sessions as specified by the specification
        if float(mapping.redfish_version) >= 1.00:
            url += '/Sessions'

        # Craft request body and header
        requestBody = {"UserName": self.connection_parameters.user_name  , "Password": self.connection_parameters.password}
        header = {'Content-type': 'application/json'}
        # =======================================================================
        # Tortilla seems not able to provide the header of a post request answer.
        # However this is required by redfish standard to get X-Auth-Token.
        # So jump to "requests" library to get the required token.
        # TODO : Patch tortilla to handle this case.
        # =======================================================================
        # sessionsUrl = tortilla.wrap("https://10.3.222.104/rest/v1/Sessions", debug=TORTILLADEBUG)
        # sessions = sessionsUrl.post(verify=self.verify_cert, data=requestBody)
        auth = requests.post(url,
                             data=json.dumps(requestBody),
                             headers=header,
                             verify=self.connection_parameters.verify_cert
                            )
 
        # =======================================================================
        # TODO : Manage exception with a class.
        # =======================================================================
        if auth.status_code != 201:
            raise exception.AuthenticationFailureException("Login request return an invalid status code")
            #sysraise "Error getting token", auth.status_code

        self.connection_parameters.auth_token = auth.headers.get("x-auth-token")
        self.connection_parameters.user_uri = auth.headers.get("location")
        config.logger.debug("x-auth-token : %s", self.connection_parameters.auth_token)
        config.logger.debug("user session : %s", self.connection_parameters.user_uri)
        return True

    def logout(self):
        # Craft full url
        url = self.connection_parameters.user_uri

        # Craft request header
        header = {"Content-type": "application/json",
                  "x-auth-token": self.connection_parameters.auth_token
                 }

        logout = requests.delete(url, headers=header,
                                 verify=self.connection_parameters.verify_cert
                                )

        if logout.status_code == 200:
            config.logger.info("Logout successful")
        else:
            config.logger.error("Logout failed")
            raise exception.LogoutFailureException("Fail to logout properly.")


class ConnectionParameters(object):
    """Store connection parameters."""

    def __init__(self):
        pass

    @property
    def rooturl(self):
        return self.__rooturl

    @rooturl.setter
    def rooturl(self, rooturl):
        self.__rooturl = rooturl

    @property
    def user_name(self):
        return self.__user_name

    @user_name.setter
    def user_name(self, user_name):
        self.__user_name = user_name

    @property
    def password(self):
        return self.__password

    @password.setter
    def password(self, password):
        self.__password = password

    @property
    def enforceSSL(self):
        return self.__enforceSSL

    @enforceSSL.setter
    def enforceSSL(self, enforceSSL):
        self.__enforceSSL = enforceSSL

    @property
    def verify_cert(self):
        return self.__verify_cert

    @verify_cert.setter
    def verify_cert(self, verify_cert):
        self.__verify_cert = verify_cert

    @property
    def auth_token(self):
        return self.__auth_token

    @auth_token.setter
    def auth_token(self, auth_token):
        self.__auth_token = auth_token

    @property
    def user_uri(self):
        return self.__user_uri

    @user_uri.setter
    def user_uri(self, user_uri):
        self.__user_uri = user_uri
