# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
from builtins import str
from . import config
standard_library.install_aliases()


class RedfishException(Exception):
    """Base class for redfish exceptions"""
    def __init__(self, message, **kwargs):
        self.kwargs = kwargs
        self.message = message
        self.advices = None
        config.logger.error(message)


class ConnectionFailureException(RedfishException):
    def __init__(self, message, **kwargs):
        super(ConnectionFailureException, self).__init__(message, **kwargs)
        self.advices = \
            '1- Check if the url is the correct one\n' + \
            '2- Check if your device is answering on the network\n' + \
            '3- Check if your device has a valid trusted certificate.\n' + \
            '   You can use openssl to validate it using the command :\n' + \
            '   openssl s_client -showcerts -connect <server>:443\n' + \
            '4- Use option "--insecure" to connect without checking' + \
            '   certificate\n'


class InvalidRedfishContentException(RedfishException):
    def __init__(self, message, **kwargs):
        super(InvalidRedfishContentException, self).__init__(message, **kwargs)
        self.advices = \
            '1- Check if the url is the correct one\n' + \
            '   Most of the time you are not pointing to the rest API\n'


class AuthenticationFailureException(RedfishException):
    def __init__(self, message, **kwargs):
        super(AuthenticationFailureException, self).__init__(message, **kwargs)
        self.message += str(kwargs['code'])
        self.queryAnswer = kwargs['queryAnswer']
        if kwargs['code'] == 400:
            self.message += ': ' + self.queryAnswer['Messages'][0]['MessageID']
            self.advices = '1- Check your credentials\n'
        self.message += '\n'


class LogoutFailureException(RedfishException):
    pass
