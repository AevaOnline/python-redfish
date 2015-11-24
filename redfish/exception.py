# -*- coding: utf-8 -*-


class RedfishException(Exception):
    """Base class for redfish exceptions"""
    def __init__(self, message=None, **kwargs):
        self.kwargs = kwargs
        self.message = message



class AuthenticationFailureException(RedfishException):
    pass

class LogoutFailureException(RedfishException):
    pass