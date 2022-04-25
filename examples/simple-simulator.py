# coding=utf-8

""" Simple example to use python-redfish with HPE simulator """
# Works fine after the declaration of the default server with
# redfish-client config add default \
#   https://ilorestfulapiexplorer.ext.hpe.com/redfish/v1

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library

# Import necessary libraries
import os
import sys
import json
import redfish
standard_library.install_aliases()

# Get $HOME environment.
HOME = os.getenv('HOME')

if HOME == '':
    print("$HOME environment variable not set, please check your system")
    sys.exit(1)

try:
    with open(HOME + "/.redfish/inventory") as json_data:
        config = json.load(json_data)
        json_data.close()
except IOError as e:
    print("Please create a json configuration file")
    print(e)
    sys.exit(1)

URL = config["Managers"]["default"]["url"]
USER_NAME = config["Managers"]["default"]["login"]
PASSWORD = config["Managers"]["default"]["password"]

''' remoteMgmt is a redfish.RedfishConnection object '''
try:
    remote_mgmt = redfish.connect(URL,
                                  USER_NAME,
                                  PASSWORD,
                                  simulator=True,
                                  verify_cert=False,
                                  enforceSSL=False)
except redfish.exception.RedfishException as e:
    sys.stderr.write(e.message)
    sys.stderr.write(e.advices)
    sys.exit(1)


print("Redfish API version : {} \n".format(remote_mgmt.get_api_version()))
print("UUID : {} \n".format(remote_mgmt.Root.get_api_UUID()))
print("System 1 :\n")
print("Bios version : {}\n".format(
    remote_mgmt.Systems.systems_dict["1"].get_bios_version()))
print("System 2 :\n")
print("Serial Number : {}\n".format(
    remote_mgmt.Systems.systems_dict["1"].get_parameter("SerialNumber")))
