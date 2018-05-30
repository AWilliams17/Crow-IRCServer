from configparser import ConfigParser
from .sentry_exceptions import *
from inspect import getmembers
from os import path


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
        fields = []

        for name, obj in getmembers(cls, lambda x: type(x) is type(SentrySection)):
            if not isinstance(cls, obj):  # ignore the metaclass, only get section classes
                fields.append(obj)

        cls.fields = fields

        super().__init__(name, bases, d)


class SentryConfig(metaclass=SentryConfigMetaclass):
    __ini_full_path = None
    __output = []

    def start(self, ini_folder, ini_name):
        self.__ini_full_path = path.join(ini_folder, ini_name)

        if not path.exists(self.__ini_full_path):
            self.__output.append("No configuration file was found. A new one will be created with default values.")
            self.__flush_config()  # create a new config

        self.__read_config()

    def __read_config(self):
        print("Read Config")

    def __flush_config(self):
        print("Flush Config")

