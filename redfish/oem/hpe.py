# coding=utf-8
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library

import re
from ..types import Base, BaseCollection, Device
standard_library.install_aliases()

# Global variable


class NetworkAdaptersCollection(BaseCollection):
    '''Class to manage redfish hpe oem NetworkAdaptersCollection data.'''
    def __init__(self, url, connection_parameters):
        super(NetworkAdaptersCollection, self).__init__(url,
                                                        connection_parameters)
        self.network_adapters_dict = {}

        for link in self.links:
            index = re.search(r'NetworkAdapters/(\w+)', link)
            self.network_adapters_dict[index.group(1)] = NetworkAdapters(
                link, connection_parameters)


class NetworkAdapters(Device):
    '''Class to manage redfish hpe oem NetworkAdapters data.'''

    def get_mac(self):
        '''Get NetworkAdapters mac address

        :returns:  mac adresses or "Not available"
        :rtype: list

        '''

        macaddresses = []

        try:
            for port in self.data.PhysicalPorts:
                mac = port['MacAddress']
                macaddresses.append(mac)

            return macaddresses
        except AttributeError:
            return "Not available"

    def get_structured_name(self):
        '''Get NetworkAdapters StructuredName

        :returns: StructuredName or "Not available"
        :rtype: string

        '''
        try:
            return self.data.StructuredName
        except AttributeError:
            return "Not available"

    def get_uefi_path(self):
        '''Get networkadapters uefi path

        :returns: UEFIDevicePath or "Not available"
        :rtype: string

        '''
        try:
            return self.data.UEFIDevicePath
        except AttributeError:
            return "Not available"


class SmartStorage(Base):
    '''Class to manage redfish hpe oem SmartStorage data.'''
    def __init__(self, url, connection_parameters):
        super(SmartStorage, self).__init__(url, connection_parameters)
        try:
            self.array_controllers_collection = \
                ArrayControllersCollection(
                    self.get_link_url('ArrayControllers', self.data.Links),
                    connection_parameters)

        except AttributeError:
            # This means we don't have ArrayControllers
            self.array_controllers_collection = None


class ArrayControllersCollection(BaseCollection):
    '''Class to manage redfish hpe oem ArrayControllersCollection data.'''
    def __init__(self, url, connection_parameters):
        super(ArrayControllersCollection, self).__init__(url,
                                                         connection_parameters)
        self.array_controllers_dict = {}

        for link in self.links:
            index = re.search(r'ArrayControllers/(\w+)', link)
            self.array_controllers_dict[index.group(1)] = ArrayControllers(
                link, connection_parameters)


class ArrayControllers(Device):
    '''Class to manage redfish hpe oem ArrayControllers data.'''
    def __init__(self, url, connection_parameters):
        super(ArrayControllers, self).__init__(url, connection_parameters)
        try:
            self.logical_drives_collection = \
                LogicalDrivesCollection(
                    self.get_link_url('LogicalDrives', self.data.Links),
                    connection_parameters)

        except AttributeError:
            # This means we don't have ArrayControllers
            self.logical_drives_collection = None

        try:
            self.physical_drives_collection = \
                PhysicalDrivesCollection(
                    self.get_link_url('PhysicalDrives', self.data.Links),
                    connection_parameters)

        except AttributeError:
            # This means we don't have ArrayControllers
            self.physical_drives_collection = None


class LogicalDrivesCollection(BaseCollection):
    '''Class to manage redfish hpe oem LogicalDrivesCollection data.'''
    def __init__(self, url, connection_parameters):
        super(LogicalDrivesCollection, self).__init__(url,
                                                      connection_parameters)
        self.logical_drives_dict = {}

        for link in self.links:
            index = re.search(r'LogicalDrives/(\w+)', link)
            self.logical_drives_dict[index.group(1)] = LogicalDrives(
                link, connection_parameters)


class LogicalDrives(Device):
    '''Class to manage redfish hpe oem LogicalDrives data.'''
    def get_capacity(self):
        '''Get Logical drive capacity

        :returns: Logical drive capacity or "Not available"
        :rtype: string

        '''
        try:
            return self.data.CapacityMiB
        except AttributeError:
            return "Not available"

    def get_raid(self):
        '''Get Logical drive raid configuration

        :returns: Logical drive raid configuration or "Not available"
        :rtype: string

        '''
        try:
            return self.data.Raid
        except AttributeError:
            return "Not available"


class PhysicalDrivesCollection(BaseCollection):
    '''Class to manage redfish hpe oem PhysicalDrivesCollection data.'''
    def __init__(self, url, connection_parameters):
        super(PhysicalDrivesCollection, self).__init__(url,
                                                       connection_parameters)
        self.physical_drives_dict = {}

        for link in self.links:
            index = re.search(r'DiskDrives/(\w+)', link)
            self.physical_drives_dict[index.group(1)] = DiskDrives(
                link, connection_parameters)


class DiskDrives(Device):
    '''Class to manage redfish hpe oem DiskDrives data.'''
    def get_capacity(self):
        '''Get Logical drive capacity

        :returns: Logical drive capacity or "Not available"
        :rtype: string

        '''
        try:
            return self.data.CapacityMiB
        except AttributeError:
            return "Not available"


class StorageEnclosures(Device):
    '''Class to manage redfish hpe oem StorageEnclosures data.'''
    pass
