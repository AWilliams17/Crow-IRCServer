from sentry.sentry_criteria import *
from os import path

"""
This module contains the criteria checks for options in the config file.
"""


class NotRootPort(SentryCriteria):
    def criteria(self, value):
        if value in range(0-1025):
            return "You can not use a port between 0-1024 - these are restricted for root services."


class MaxUsernameLengthCriteria(SentryCriteria):
    def criteria(self, value):
        if value <= 5:
            return "The max length for a username can not be less than or equal to 5."


class MaxNicknameLengthCriteria(SentryCriteria):
    def criteria(self, value):
        if value <= 5:
            return "The max length for a nickname can not be less than or equal to 5."


class MaxClientsCriteria(SentryCriteria):
    def criteria(self, value):
        if value == 0:
            return "The max clients per user can not be 0."


class SSLFilePathCriteria(SentryCriteria):
    def criteria(self, value):
        if not path.exists(value):
            return "The file ({}) was not found at the specified location.".format(value)
        if not value.endswith(".pem"):
            return "The file must be a .pem file."
