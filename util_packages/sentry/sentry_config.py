from configparser import ConfigParser
from .sentry_exceptions import *
from inspect import getmembers


class SentryOption:
    def __init__(self, default=None, criteria=None, criteria_desc=None):
        if type(criteria) is not list and criteria is not None:
            criteria = [].append(criteria)
        if criteria is not None and criteria_desc is None:
            raise CriteriaDescriptionError
        self.default = default
        self.criteria = criteria
        self.criteria_error = criteria_desc


class SentrySection:
    def __init__(self, section_name):
        self.section_name = section_name

    def set_option(self, option_name, value):
        if hasattr(self, option_name):
            option = getattr(self, option_name)
            if option.criteria is not None:
                for validator in option.criteria:
                    if not validator(value):
                        raise CriteriaNotMetError(option.criteria_desc)
            setattr(self, option_name, value)
        raise KeyError("Option {} was not found in the section class {}.".format(option_name, self.section_name))

    def get_option(self, option_name):
        if hasattr(self, option_name):
            option = getattr(self, option_name)
            option_set = type(option) is SentryOption
            if option_set:
                return option
            if option.default is not None:
                return option.default
            raise MissingOptionError(self.section_name, option_name)
        raise KeyError("Option {} was not found in the section class {}.".format(option_name, self.section_name))


class SentryConfigMetaclass(type):
    def __init__(cls, name, bases, d):
        print(d)
        print(bases)

        for option_name, option_object in getmembers(cls, lambda x: isinstance(x, SentrySection)):
            print("Test")

        super().__init__(name, bases, d)


class SentryConfig(metaclass=SentryConfigMetaclass):
    def read_config(self, ini_path):
        pass

