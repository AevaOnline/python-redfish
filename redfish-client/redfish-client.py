#!/usr/bin/python

# coding=utf-8

"""
redfish-client

Usage:
  redfish-client.py [options] config add <manager_name> <manager_url> [<login>] [<password>]
  redfish-client.py [options] config del <manager_name>
  redfish-client.py [options] config modify <manager_name> (url | login | password) <changed_value>
  redfish-client.py [options] config show
  redfish-client.py [options] config showall
  redfish-client.py (-h | --help)
  redfish-client.py --version
  

Options:
  -h --help     Show this screen.
  --version     Show version.
  --conf_file FILE      Configuration file [default: ~/.redfish.conf].


config commands manage the configuration file.

"""

import os
import sys
import json
import pprint
import docopt


class ConfigFile(object):
    def __init__(self, config_file):
	self._config_file = config_file
        # read json file
        try:
            with open(self._config_file) as json_data:
                self.data = json.load(json_data)
                json_data.close()
        except (ValueError, IOError):
            self.data = {"Managers":{}}

    def save(self):
        try:
            with open(self._config_file , 'w') as json_data:
                json.dump(self.data, json_data)
                json_data.close()
        except IOError as e:
	    print(e.msg)
	    sys.exit(1)
    
    def add_manager(self, manager_name, url, login, password):
        self.data['Managers'][manager_name] = {}
        self.data['Managers'][manager_name]['url'] = url
        if login != None:
            self.data['Managers'][manager_name]['login'] = login
        if password != None:
            self.data['Managers'][manager_name]['password'] = password
    
    def get_managers(self):
        managers = []
        for manager in self.data['Managers']:
                managers += [manager]
        return(managers)
    
    def get_manager_info(self, manager):
        info = {}
        url=self.data['Managers'][manager]['url']
        login=self.data['Managers'][manager]['login']
        password=self.data['Managers'][manager]['password']
        info={'url':url, 'login':login, 'password':password}
        return(info)    

class RedfishClientException(Exception):
    """Base class for redfish client exceptions"""
    def __init__(self, message=None, **kwargs):
        self.kwargs = kwargs
        self.message = message  


if __name__ == '__main__':
    # Functions
    def show_manager(all=False):
        print("Managers configured :")
        for manager in conf_file.get_managers():
            print(manager)
            if all == True:
                info = conf_file.get_manager_info(manager)
                print("\tUrl : {}".format(info['url']))
                print("\tLogin : {}".format(info['login']))
                print("\tPassword : {}".format(info['password']))
    
    # Get $HOME environment.
    HOME = os.getenv('HOME')

    if HOME == '':
        print("$HOME environment variable not set, please check your system")
        sys.exit(1)

    arguments = docopt.docopt(__doc__, version='redfish-client 0.1')
    print(arguments)

    arguments['--conf_file'] = arguments['--conf_file'].replace('~', HOME)

    conf_file = ConfigFile(arguments['--conf_file'])


    if arguments['config'] == True:
        if arguments['show'] == True:
            show_manager()
        elif arguments['showall'] == True:
            show_manager(True)
        elif arguments['add'] == True:
            conf_file.add_manager(arguments['<manager_name>'],
                                  arguments['<manager_url>'],
                                  arguments['<login>'],
                                  arguments['password'])
            pprint.pprint(conf_file.data)

	conf_file.save()


    sys.exit(0)
