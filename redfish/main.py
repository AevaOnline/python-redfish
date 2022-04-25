# coding=utf-8
#
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
absent based upon the implementation
(e.g. there might be no /redfish/v1/Systems collection on something
that doesn't have compute nodes.)

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

When POSTing to create a resource (e.g. create an account or session) the
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
* some properties are schemed to allow both null and another type like string
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
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
from builtins import object

import json
import requests
from . import config
from . import standard
from . import mapping
from . import exception
standard_library.install_aliases()
from urllib.parse import urlparse, urljoin, urlunparse  # noqa: E402

"""Function to wrap RedfishConnection"""


def connect(
        url,
        user,
        password,
        simulator=False,
        enforceSSL=True,
        verify_cert=True):

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
        # Specify a name for the logger as recommended by the logging
        # documentation. However for strange reason requests logs are not
        # anymore captured in the log file.
        # TODO : Check strange behavior about requests logs.
        config.logger = config.initialize_logger(config.REDFISH_LOGFILE,
                                                 config.CONSOLE_LOGGER_LEVEL,
                                                 config.FILE_LOGGER_LEVEL,
                                                 __name__)

        config.logger.info("Initialize python-redfish")

        self.connection_parameters = ConnectionParameters()
        self.connection_parameters.rooturl = url
        self.connection_parameters.user_name = user
        self.connection_parameters.password = password
        self.connection_parameters.enforceSSL = enforceSSL
        self.connection_parameters.verify_cert = verify_cert

        # Use a mockup or not (like the DMTF or HPE one)
        self.__simulator = simulator

        # Session attributes
        self.connection_parameters.auth_token = None
        self.connection_parameters.user_uri = None

        rooturl = urlparse(self.connection_parameters.rooturl)

        # Enforce ssl
        if self.connection_parameters.enforceSSL is True:
            config.logger.debug("Enforcing SSL")
            rooturl = rooturl._replace(scheme=type(rooturl.scheme)("https"))
            self.connection_parameters.rooturl = rooturl.geturl()

        # Verify cert
        if self.connection_parameters.verify_cert is False:
            config.logger.info("Certificat is not checked, " +
                               "this is insecure and can allow" +
                               " a man in the middle attack")

        config.logger.debug("Root url : %s",
                            self.connection_parameters.rooturl)
        self.Root = standard.Root(self.connection_parameters.rooturl,
                                  self.connection_parameters)

        config.logger.info("API Version : %s", self.get_api_version())
        mapping.redfish_version = self.get_api_version()
        mapping.redfish_root_name = self.Root.get_name()

        # Instantiate a global mapping object to handle
        # Redfish version variation
        mapping.redfish_mapper = mapping.RedfishVersionMapping(
            self.get_api_version(), self.Root.get_name())

        # Now we need to login otherwise we are not allowed to extract data
        if self.__simulator is False:
            try:
                config.logger.info("Login to %s", rooturl.netloc)
                self.login()
                config.logger.info("Login successful")
            except "Error getting token":
                config.logger.error("Login fail, fail to get auth token")
                raise exception.AuthenticationFailureException(
                    "Fail to get an auth token.")

        # Structure change with mockup 1.0.0, there is no links
        # section anymore.
        # ===================================================================
        # TODO : Add a switch to allow both structures
        # ===================================================================

        # standard
        # Gen-Z simulator has no SessionService for now so handle this case
        try:
            self.SessionService = standard.SessionService(
                self.Root.get_link_url(
                    mapping.redfish_mapper.map_sessionservice()),
                self.connection_parameters)
        except AttributeError:
            self.SessionService = None

        # Moonshot m510 cartridge has neither Managers nor Chassis, so handle
        # this case in the code.
        # Note : m510 ilo firmware is in an early stage, this state could be
        # temporary.
        try:
            self.Managers = standard.ManagersCollection(
                self.Root.get_link_url("Managers"),
                self.connection_parameters)
        except AttributeError:
            self.Managers = None

        self.Systems = standard.SystemsCollection(
            self.Root.get_link_url("Systems"),
            self.connection_parameters)

        try:
            self.Chassis = standard.ChassisCollection(
                self.Root.get_link_url("Chassis"),
                self.connection_parameters)
        except AttributeError:
            self.Chassis = None

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
            mapping.redfish_mapper.map_sessionservice())

        # Handle login with redfish 1.00, url must be :
        # /rest/v1/SessionService/Sessions as specified by the specification
        if float(mapping.redfish_version) >= 1.00:
            url = urljoin(url, "Sessions")

        config.logger.debug("Login URL : %s" % url)
        # Craft request body and header
        requestBody = {"UserName": self.connection_parameters.user_name,
                       "Password": self.connection_parameters.password}
        config.logger.debug(requestBody)
        headers = self.connection_parameters.headers
        # ====================================================================
        # Tortilla seems not able to provide the header of a post request
        # answer.
        # However this is required by redfish standard to get X-Auth-Token.
        # So jump to "requests" library to get the required token.
        # TODO : Patch tortilla to handle this case.
        # ====================================================================
        # sessionsUrl = tortilla.wrap(
        #     "https://10.3.222.104/rest/v1/Sessions", debug=TORTILLADEBUG)
        # sessions = sessionsUrl.post(
        #     verify=self.verify_cert, data=requestBody)
        auth = requests.post(url,
                             data=json.dumps(requestBody),
                             headers=headers,
                             verify=self.connection_parameters.verify_cert)

        # =======================================================================
        # TODO : Manage exception with a class.
        # =======================================================================
        if auth.status_code != 201:
            try:
                answer = auth.json()
            except ValueError:
                answer = ""
            raise exception.AuthenticationFailureException(
                "Login request return an invalid status code ",
                code=auth.status_code, queryAnswer=answer)

        self.connection_parameters.auth_token = auth.headers.get(
            "x-auth-token")
        self.connection_parameters.user_uri = auth.headers.get("location")
        config.logger.debug("x-auth-token : %s",
                            self.connection_parameters.auth_token)
        config.logger.debug("user session : %s",
                            self.connection_parameters.user_uri)
        return True

    def logout(self):
        # Craft full url
        url = self.connection_parameters.user_uri

        # Craft request header
        headers = self.connection_parameters.headers

        logout = requests.delete(url,
                                 headers=headers,
                                 verify=self.connection_parameters.verify_cert)

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

    @property
    def headers(self):
        # Host header is set by request or tortilla
        url = urlparse(self.__rooturl)
        origin = urlunparse((url.scheme, url.netloc, '', '', '', ''))
        headers = {'OData-Version': '4.0',
                   'Content-type': 'application/json',
                   'Accept': 'application/json',
                   'Origin': origin,
                   'User-Agent': 'python-redfish'}
        if self.auth_token:
            headers.update({'x-auth-token': self.auth_token})
        return headers
