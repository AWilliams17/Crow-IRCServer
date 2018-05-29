from configparser import ConfigParser
from inspect import getmembers, isclass


class SentryOption:
    def __init__(self, default=None, criteria=None, criteria_desc=None):
        if type(criteria) is not list and criteria is not None:
            criteria = [].append(criteria)
        if criteria is not None and criteria_desc is None:
            raise TypeError("An option can not have criteria to meet without detailing what that criteria is.")
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
                        raise ValueError(option.criteria_error)
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
            raise ValueError("The option {} in section class {} has not been set nor does it have a default value.".format(option_name, self.section_name))
        raise KeyError("Option {} was not found in the section class {}.".format(option_name, self.section_name))


class SentryConfigMetaclass(type):
    def __init__(cls, name, bases, d):

        for option_name, option_object in getmembers(cls, lambda x: isinstance(x, SentrySection)):
            print("Test")

        super().__init__(name, bases, d)


class SentryConfig(metaclass=SentryConfigMetaclass):
    pass
    #def __init__(self, ini_path):
    #    self.ini_path = ini_path


