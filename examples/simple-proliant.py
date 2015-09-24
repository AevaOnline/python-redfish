# coding=utf-8

""" Simple example to use python-redfish on HP Proliant servers """

import os
import sys
import json
import redfish

# Get $HOME environment.
HOME = os.getenv('HOME')

if HOME == '':
    print("$HOME environment variable not set, please check your system")
    sys.exit(1)

try:
    with open(HOME + "/.redfish.conf") as json_data:
        config = json.load(json_data)
        json_data.close()
except IOError as e:
    print("Please create a json configuration file")
    print(e)
    sys.exit(1)

URL = config["Nodes"]["default"]["url"]
USER_NAME = config["Nodes"]["default"]["login"]
PASSWORD = config["Nodes"]["default"]["password"]

''' remote_mgmt is a redfish.RedfishConnection object '''
remote_mgmt = redfish.connect(URL, USER_NAME, PASSWORD, verify_cert=False)

print ("Redfish API version : %s \n" % remote_mgmt.get_api_version())

# Uncomment following line to reset the blade !!! 
#remote_mgmt.Systems.systems_list[0].reset_system()

# TODO : create an attribute to link the managed system directly
#        and avoid systems_list[0]
#        --> will be something like :
#        remote_mgmt.Systems.systems_list[0] = remote_mgmt.Systems.managed_system

print("Bios version : {}\n".format(remote_mgmt.Systems.systems_list[0].get_bios_version()))

print("Serial Number : {}\n".format(remote_mgmt.Systems.systems_list[0].get_serialnumber()))

remote_mgmt.logout()
