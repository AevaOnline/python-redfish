# coding=utf-8

""" Simple example to use python-redfish with DMTF simulator """

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

''' remoteMgmt is a redfish.RedfishConnection object '''
remote_mgmt = redfish.connect(URL, USER_NAME, PASSWORD,
                             simulator=True, enforceSSL=False)

print ("Redfish API version : {} \n".format(remote_mgmt.get_api_version()))
print ("UUID : {} \n".format(remote_mgmt.Root.get_api_UUID()))
print ("Bios version : {}\n".format(remote_mgmt.Systems.systems_list[0].get_bios_version()))

#print remoteMgmt.get_api_link_to_server()
