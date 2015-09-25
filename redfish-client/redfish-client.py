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
        # read json file
        try:    
            with open(config_file) as json_data:
                self.data = json.load(json_data)
                json_data.close()
        except IOError as e:
            self.data = {"Nodes":{}}

  

if __name__ == '__main__':
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
        if arguments['showall'] == True:
            pprint.pprint(conf_file.data)
        elif arguments['add'] == True:
            conf_file.data['Nodes'][arguments['<manager_name>']] = {}
            conf_file.data['Nodes'][arguments['<manager_name>']]['url'] = arguments['<manager_url>']
            if arguments['<login>'] != None:
                 conf_file.data['Nodes'][arguments['<manager_name>']]['login'] = arguments['<login>']
            if arguments['<login>'] != None:
                 conf_file.data['Nodes'][arguments['<manager_name>']]['password'] = arguments['<password>']
            pprint.pprint(conf_file.data)
            
    