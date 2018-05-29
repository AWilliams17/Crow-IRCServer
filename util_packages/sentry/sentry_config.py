from configparser import ConfigParser
from inspect import getmembers


class SentryOption:
    def __init__(self, default=None, criteria=None, criteria_error=None):
        self.default = default
        self.criteria = criteria
        self.criteria_error = criteria_error


class _SentrySectionMetaclass(type):
    def __init__(cls, name, bases, d):

        print(cls.__dict__.items())

        super(_SentrySectionMetaclass, cls).__init__(name, bases, d)


class SentrySection(metaclass=_SentrySectionMetaclass):
    def __init__(self):
        pass


class SentryConfig:
    def __init__(self, config_file_path):
        self.config_file = config_file_path
        self.config_parser = ConfigParser()
