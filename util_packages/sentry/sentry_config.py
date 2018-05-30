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
        self.criteria_desc = criteria_desc


class _SentrySectionMetaclass(type):
    def __init__(cls, name, bases, d):

        section_options = []

        for name, obj in getmembers(cls, lambda x: isinstance(x, SentryOption)):
            obj.option_name = name
            section_options.append(obj)

        cls._section_options = section_options

        super().__init__(name, bases, d)


class SentrySection(metaclass=_SentrySectionMetaclass):
    def __init__(self):
        self.section_name = None  # automatically set

    def set_option(self, option_name, value):
        if not hasattr(self, option_name):
            raise KeyError("Option {} was not found in the section class {}.".format(option_name, self.section_name))
        option = getattr(self, option_name)
        if isinstance(option, SentryOption) and option.criteria is not None:
            for validator in option.criteria:
                if not validator(value):
                    raise CriteriaNotMetError(option.criteria_desc)
        setattr(self, option_name, value)

    def get_option(self, option_name):
        if not hasattr(self, option_name):
            raise KeyError("Option {} was not found in the section class {}.".format(option_name, self.section_name))
        option = getattr(self, option_name)
        option_already_set = not isinstance(option, SentryOption)
        if option_already_set:
            return option
        if option.default is not None:
            return option.default
        raise MissingOptionError(self.section_name, option_name)


class _SentryConfigMetaclass(type):
    def __init__(cls, name, bases, d):

        sections = {}

        for name, obj in getmembers(cls, lambda x: type(x) is type(SentrySection)):
            if obj is not cls:
                obj.section_name = name
                sections[name] = obj

        cls._sections = sections

        super().__init__(name, bases, d)


class SentryConfig(metaclass=_SentryConfigMetaclass):
    def __init__(self, ini_path):
        self._ini_path = ini_path
        self._config = ConfigParser()

    def read_config(self):
        self._config.read(self._ini_path)
        config_sections = {x: [z for z in self._config.items(x)] for x in self._config.sections()}

        for section_name, section_object in self._sections.items():
            if section_name not in config_sections:
                pass
            config_options = dict(config_sections[section_name])
            current_section = section_object
            current_options = current_section.section_options
            for option in current_options:
                if option.option_name not in config_options:
                    pass
                config_option_val = config_options[option.option_name]
                option.set_option(config_option_val)

    def flush_config(self):
        with open(self._ini_path, "w") as ini_file:
            for section_name, section_object in self._sections.items():
                if not self._config.has_section(section_name):
                    self._config.add_section(section_name)
                current_section = section_object
                current_options = current_section.section_options
                for option in current_options:
                    option_value = str(current_section.get_option(current_section, option.option_name))
                    self._config.set(section_name, option.option_name, option_value)
            self._config.write(ini_file)
