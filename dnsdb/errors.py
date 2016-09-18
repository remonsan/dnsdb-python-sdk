# -*- coding: utf-8 -*-
from __future__ import unicode_literals


class DnsDBException(Exception):
    def __init__(self, value):
        self.value = value
        self.message = value

    def __str__(self):
        return self.value


class AuthenticationError(DnsDBException):
    @staticmethod
    def require_login_error():
        return AuthenticationError('Require login')


class APIServerError(DnsDBException):
    def __init__(self):
        super(APIServerError, self).__init__("API Server error")
