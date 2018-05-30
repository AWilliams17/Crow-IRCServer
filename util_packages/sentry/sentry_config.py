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


class SentrySectionMetaclass(type):
    def __init__(cls, name, bases, d):

        section_options = []

        for name, obj in getmembers(cls, lambda x: isinstance(x, SentryOption)):
            obj.option_name = name
            section_options.append(obj)

        cls.section_options = section_options

        super().__init__(name, bases, d)


class SentrySection(metaclass=SentrySectionMetaclass):
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


class SentryConfig:
    _ini_full_path = None
    _output = []
    _sections = {}
    _config = ConfigParser()

    def start(self, ini_folder, ini_name):
        self._ini_full_path = path.join(ini_folder, ini_name)
        for name, obj in getmembers(self, lambda x: type(x) is type(SentrySection)):
            if obj is not self.__class__:
                obj.section_name = name
                self._sections[name] = obj

        if not path.exists(self._ini_full_path):
            self._output.append("No configuration file was found. A new one will be created with default values.")
            self._flush_config()  # create a new config with them

        self._flush_config()
        #self._read_config()

    def _read_config(self):
        self._config.read(self._ini_full_path)
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

    def _flush_config(self):
        with open(self._ini_full_path, "w") as ini_file:
            for section_name, section_object in self._sections.items():
                if not self._config.has_section(section_name):
                    self._config.add_section(section_name)
                current_section = section_object
                current_options = current_section.section_options
                for option in current_options:
                    option_value = str(current_section.get_option(current_section, option.option_name))
                    self._config.set(section_name, option.option_name, option_value)
            self._config.write(ini_file)
