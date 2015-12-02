# -*- coding: utf-8 -*-
import sys
import config

class RedfishException(Exception):
    """Base class for redfish exceptions"""
    def __init__(self, message=None, **kwargs):
        self.kwargs = kwargs
        self.message = message


class AuthenticationFailureException(RedfishException):
    def __init__(self, message=None, **kwargs):
        super(AuthenticationFailureException, self).__init__(message=None, **kwargs)
        config.logger.error(message)
        # TODO
        # Give a bit more details about the failure (check login etc...) 
        sys.exit(1)
        
class LogoutFailureException(RedfishException):
    pass
