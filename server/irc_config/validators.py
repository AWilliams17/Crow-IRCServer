from sentry import SentryCriteria

"""
This module contains the criteria checks for options in the config file.
"""


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
