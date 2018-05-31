from configparser import ConfigParser
from .sentry_exceptions import *
from .sentry_criteria import SentryCriteria
from inspect import getmembers


class _SentryConfigMetaclass(type):
    def __init__(cls, name, bases, d):

        sections = {}

        for section_name, section_object in getmembers(cls, lambda x: type(x) is type(SentrySection)):
            if section_object is not cls.__class__:
                section_object.name = section_name
                section_object.options = {}
                section_object = section_object()
                setattr(cls, section_name, section_object)

                for option_name, option_object in getmembers(section_object, lambda x: isinstance(x, SentryOption)):
                    option_object.name = option_name
                    section_object.options[option_name] = option_object
                sections[section_name] = section_object

        cls.sections = sections

        super().__init__(name, bases, d)


class SentryOption:
    def __init__(self, default=None, criteria=None, description=None):
        if type(criteria) is not list:
            if criteria is None:
                criteria = []
            else:
                criteria = [criteria]

        for criteria_obj in criteria:
            if not isinstance(criteria_obj, SentryCriteria):
                criteria[criteria.index(criteria_obj)] = criteria_obj()

        self.default = default
        self.criteria = criteria
        self.description = description

    def criteria_met(self, value):
        for criteria in self.criteria:
            return criteria(self.name, value)

    def about(self):
        if self.description is None:
            return "No description for this option exists."
        return self.description


class SentrySection:
    def __init__(self):
        self.name = None  # automatically set

    def set_option(self, option_name, value):
        if not hasattr(self, option_name):
            raise MissingOptionError(self.name, option_name)

        option = getattr(self, option_name)

        if isinstance(option, SentryOption):
            converted = option.criteria_met(value)
            if converted is not None:
                value = converted

        setattr(self, option_name, value)

    def set_default(self, option_name):
        option = getattr(self, option_name)
        if isinstance(option, SentryOption):
            if option.default is None:
                raise NoDefaultGivenError(self.name, option_name)
            self.set_option(option_name, option.default)

    def get_option(self, option_name):
        if not hasattr(self, option_name):
            raise MissingOptionError(self.name, option_name)

        option = getattr(self, option_name)
        option_already_set = not isinstance(option, SentryOption)

        if option_already_set:
            return option

        if option.default is not None:
            return option.default


class SentryConfig(metaclass=_SentryConfigMetaclass):
    def __init__(self, ini_path):
        self._ini_path = ini_path
        self._config = ConfigParser()

    def read_config(self, set_default_on_fail=False):
        self._config.read(self._ini_path)
        config_sections = {x: [z for z in self._config.items(x)] for x in self._config.sections()}

        for section_name, section in self.sections.items():
            if section_name not in config_sections:
                raise MissingSectionError(self.__class__.__name__, section_name)
            config_options = dict(config_sections[section_name])

            for option in section.options:
                if option.lower() not in config_options:
                    raise MissingOptionError(section_name, option)

                config_option_val = config_options[option.lower()]
                try:
                    section.set_option(option, config_option_val)
                except CriteriaNotMetError:
                    if not set_default_on_fail:
                        raise
                    section.set_default(option)

    def flush_config(self):
        with open(self._ini_path, "w") as ini_file:
            for section_name, section in self.sections.items():
                if not self._config.has_section(section_name):
                    self._config.add_section(section_name)

                for option in section.options:
                    option_value = str(section.get_option(option))
                    self._config.set(section_name, option, option_value)

            self._config.write(ini_file)
