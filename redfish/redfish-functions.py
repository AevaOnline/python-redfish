
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

Provides functions for using the Redfish RESTful API.

"""

import ssl
import urllib2
from urlparse import urlparse
import httplib
import base64
import json
import hashlib
import gzip
import StringIO
import sys
from python-redfish import connection

class RedfishOperation(object):

    def __init__(self):
        super(RedFishOperation, self).__init__()
        # XXX add members, we're going to have to cache
    	conn = RedfishConnection()
	authen = {'Password': conn.iLO_password, 'UserName': conn.iLO_loginname}
	conn.rest_post(conn.host, '/rest/v1/sessions', None, json.dump(authen),
            conn.iLO_loginname, conn.iLO_password)

    # noinspection PyPep8Naming
    def reset_server(host, iLO_loginname, iLO_password):
        print('Reset a server')
    
        # for each system in the systems collection at /rest/v1/Systems
        for status, headers, system, memberuri in collection(host, '/rest/v1/Systems', None, iLO_loginname, iLO_password):
    
            # verify expected type
            # hint:  don't limit to version 0 here as we will rev to 1.0 at some point hopefully with minimal changes
            assert(get_type(system) == 'ComputerSystem.0' or get_type(system) == 'ComputerSystem.1')
    
            # verify it supports POST
            assert(operation_allowed(headers, 'POST'))
    
            action = dict()
            action['Action'] = 'Reset'
            action['ResetType'] = 'ForceRestart'
    
            # perform the POST action
            print('POST ' + json.dumps(action) + ' to ' + memberuri)
            status, headers, response = rest_post(host, memberuri, None, action, iLO_loginname, iLO_password)
            print('POST response = ' + str(status))
            print_extended_error(response)
    
            # point made...quit
            break
