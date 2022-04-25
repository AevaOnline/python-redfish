#!/usr/bin/env python
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# THIS FILE IS MANAGED BY THE GLOBAL REQUIREMENTS REPO - DO NOT EDIT
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
import os
import sys
import fileinput
import re
import pprint
import distutils
import setuptools
from setuptools import Distribution
from setuptools.command.install import install

# Trick to allow pip installation
major, minor = sys.version_info[:2]
if major == 2:
    import ConfigParser as configparser
else:
    import configparser

# In python < 2.7.4, a lazy loading of package `pbr` will break
# setuptools if some other modules registered functions in `atexit`.
# solution from: http://bugs.python.org/issue15881#msg170215
try:
    import multiprocessing  # noqa
except ImportError:
    pass


class OnlyGetScriptPath(install):
    '''Extend setuptools install class and replace run method to go through
    setuptool installation and retrieve the script path
    '''
    def run(self):
        # does not call install.run() by design
        self.distribution.install_scripts = self.install_scripts


class DataFilesHelper(object):
    '''Class to help manage data files'''
    def __init__(self):
        '''Read setup.cfg and build the required data'''
        self.data = {}
        self.setupstruc = []
        config = configparser.ConfigParser()
        config.read('setup.cfg')
        for datafile in config.options('data_files_helper'):
            src, dst = config.get('data_files_helper', datafile).split(',')
            src = self.refinesrc(src)
            dst = self.refinedst(dst)
            self.data[datafile] = {'src': src,
                                   'dst': dst,
                                   'fdst': self.calculatedst(src, dst)}
            self.update_setupstruc(src, dst)
        try:
            # Create an entry for scripts if available
            self.data['script'] = {'src': [],
                                   'fdst': [],
                                   'dst': 'bin'}
            src = config.get('files', 'scripts').split('\n')
            # print("List handled: {}\n".format(src))
            listsrc = []
            for s in src:
                if not s:
                    continue
                # print("Source handled: {}".format(s))
                listsrc.append(s)
            self.data['script']['src'] = listsrc
            self.data['script']['fdst'] = self.calculatedst(listsrc, "bin")
        except configparser.NoOptionError:
            pass
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(self.data)

    def trim(self, string):
        string = string.strip()
        string = string.strip("'")
        string = string.strip('"')
        return(string)

    def refinesrc(self, file):
        '''Refine source:
           Expend source file if needed

        :param file: source files
        :type file: string
        :returns: source files refined
        :rtype: list
        '''
        file = self.trim(file)
        if(file.endswith('/*')):
            return(self.getfiles(file.replace('/*', '')))
        else:
            return([file])

    def refinedst(self, file):
        '''Refine destination:
           Check if destination needs an exception

        :param file: destination
        :type path: string
        :returns: destination refined
        :rtype: string
        '''
        file = self.trim(file)
        if('etc' in file and self.getprefix() == '/usr'):
            return('/etc')
        else:
            return(file)

    def calculatedst(self, src, dst):
        '''Calculate the full destination path according to source and
           destination

        :param src: source files
        :type path: list
        :param dst: destination path
        :type path: string
        :returns: files with full destination
        :rtype: list
        '''
        destination = []
        for file in src:
            if(dst.startswith('/')):
                destination.append(os.path.join(dst,
                                   os.path.basename(file)))
            else:
                destination.append(os.path.join(self.getprefix(),
                                                dst,
                                                os.path.basename(file)))
        return(destination)

    def getfiles(self, path):
        '''Retrieve file list within a directory

        :param path: directory path
        :type path: string
        :returns: file list
        :rtype: list
        '''
        for root, dirs, files in os.walk(path):
            file_list = [os.path.join(root, file) for file in files]
        return(file_list)

    def getprefix(self):
        '''Retrieve setup tool calculated prefix

        :returns: prefix
        :rtype: string
        '''
        dist = Distribution({'cmdclass': {'install': OnlyGetScriptPath}})
        dist.dry_run = True  # not sure if necessary, but to be safe
        dist.parse_config_files()
        try:
            dist.parse_command_line()
        except (distutils.errors.DistutilsArgError, AttributeError):
            pass
        command = dist.get_command_obj('install')
        command.ensure_finalized()
        command.run()
        prefix = dist.install_scripts.replace('/bin', '')
        return prefix

    def update_setupstruc(self, src, dst):
        '''Create/update structure for setuptools.setup()
           like the following example.

          [('etc/', ['redfish-client/etc/redfish-client.conf']),
           ('share/redfish-client/templates',
            ['redfish-client/templates/manager_info.template',
             'redfish-client/templates/bla.template'])]
        '''
        self.setupstruc.append((dst, src))

    def getsetupstruc(self):
        '''Retrieve setup structure compatible with setuptools.setup()
           This is only to encapsulatate setupstruc property

        :returns: datafiles source and destination
        :rtype: setuptools structure
        '''
        return(self.setupstruc)


##########################################
# Functions
##########################################
def replaceAll(file, searchExp, replaceExp):
    for line in fileinput.input(file, inplace=1):
        if searchExp in line:
            line = line.replace(searchExp, replaceExp)
        sys.stdout.write(line)


def getversion():
    with open("python_redfish.egg-info/PKG-INFO", "r") as f:
        output = f.read()
    s = re.search(r'\nVersion:\s+(\S+)', output)
    return(s.group(1))


##########################################
# START
##########################################

datafiles = DataFilesHelper()

# Install software
setuptools.setup(
    setup_requires=['pbr'],
    pbr=True,
    data_files=datafiles.getsetupstruc())


if('install' in sys.argv):
    # Update conf files
    for file in datafiles.data['conf']['fdst']:
        print('Update : {}'.format(file))
        replaceAll(file, 'PBSHAREPATH',
                   os.path.dirname(datafiles.data['rfcusage']['fdst'][0]))
    # Update script files
    for file in datafiles.data['script']['fdst']:
        print('Update : {}'.format(file))
        replaceAll(file, 'PBCONFFILE', datafiles.data['conf']['fdst'][0])
        replaceAll(file, 'PBVER', getversion())
        replaceAll(file, 'PBSHAREPATH',
                   os.path.dirname(datafiles.data['rfcusage']['fdst'][0]))
