# ToDo: Add optional output to read_config and flush_config to be returned if requested.
# ToDo: Make it put the sections & options in the order in which they are defined in the config representation class
from sentry.sentry_exceptions import *
from sentry.sentry_criteria import SentryCriteria
from configparser import ConfigParser
from inspect import getmembers


class _SentryConfigMetaclass(type):
    """ This metaclass does the following:
    1: For every class in the config class derived from SentrySection, create a dict of options containing the options
    for that section. Set the name attribute of the SentrySection to be the name of the class.
    2: For all the options in the section, set the name attribute on it to be the name of the member.
    3: Now map all this into the new section dict of the config class.
    so for dicts:
        config_instance._sections = {section_name: section_instance }
        section_instance.options = { option_name: option_instance }
    """
    def __init__(cls, name, bases, d):
        sections = {}

        for section_name, section_object in getmembers(cls, lambda x: type(x) is type(SentrySection)):
            if section_object is not cls.__class__:  # so it doesn't pick up the metaclass itself
                section_object.name = section_name
                section_object.options = {}
                section_object = section_object()
                setattr(cls, section_name, section_object)

                for option_name, option_object in getmembers(section_object, lambda x: isinstance(x, SentryOption)):
                    option_object.name = option_name
                    section_object.options[option_name] = option_object
                    setattr(section_object, option_name, option_object)
                sections[section_name] = section_object

        cls._sections = sections

        super().__init__(name, bases, d)


class SentryOption:
    def __init__(self, default=None, criteria=None, description=None):
        """
        Represent an option in the config file.
        Args:
            default: The default value to use in the event of a failed validation (if set_to_defaults on fail is True)
            criteria (ServerCriteria[] | ServerCriteria): A list of criteria objects, or a single criteria object.
            the object(s) can optionally be instantiated before being passed. If they aren't instantiated, they
            automatically will be instantiated.
            description (str, optional): A description which describes what the option is for. Optional.
        """

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

    def criteria_met(self, option_name, value):
        for criteria in self.criteria:
            return criteria(option_name, value)

    def about(self):
        if self.description is None:
            return "No description for this option exists."
        return self.description


class SentrySection:
    """ Represent the section in the config. Contains the methods for manipulating the options in the section. """
    def set_option(self, option_name, value):
        if not hasattr(self, option_name):
            raise MissingOptionError(self.name, option_name)

        option = getattr(self, option_name)

        if isinstance(option, SentryOption):
            converted = option.criteria_met(option_name, value)
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

        raise NoDefaultGivenError(self.name, option_name)


class SentryConfig(metaclass=_SentryConfigMetaclass):
    def __init__(self, ini_path):
        """
        The actual configuration class representing the configuration file,
        which wraps all the sections in the configuration file.
        Args:
            ini_path (str): The path to the ini to use.
        Attributes:
            self._config: A ConfigParser instance. Automatically instantiated.
            self._sections: A mapping of all the sections and their options in the config class.
            Automatically instantiated.
        """
        self._ini_path = ini_path
        self._config = ConfigParser()
        self._sections = self._sections  # hide the unresolved attribute error. unnecessary but it bothers me.

    def read_config(self, set_default_on_fail=False):
        """
        Read all the options in the config file and set the appropriate values in the class.
        Args:
            set_default_on_fail: If True, then if an option fails to validate, it will be set to the default. If True
            and a default value does not exist, then an exception of type NoDefaultGivenError is raised.
        """
        self._config.read(self._ini_path)
        config_sections = {x: [z for z in self._config.items(x)] for x in self._config.sections()}

        for section_name, section in self._sections.items():
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
        """ Flush the configuration class into the configuration file. """
        with open(self._ini_path, "w") as ini_file:
            for section_name, section in self._sections.items():
                if not self._config.has_section(section_name):
                    self._config.add_section(section_name)

                for option in section.options:
                    try:
                        option_value = str(section.get_option(option))
                    except NoDefaultGivenError:
                        option_value = "None"
                    self._config.set(section_name, option, option_value)

            self._config.write(ini_file)
