#  ToDo: This all needs to be more thoroughly tested.
from configparser import ConfigParser, DuplicateOptionError, DuplicateSectionError
from os import path, getcwd


class ConfigReaper:
    """ This class takes an instance of another class which represents the ini file it is to read/write, and it takes
     the path and name to use for the ini. The path should be similar to the format getcwd() returns, and the ini
     name can optionally contain a leading slash and trailing .ini
     If no path is specified, the default directory is getcwd, and the default name is default.ini if no name is passed.
     """
    def __init__(self, config_instance, ini_path=None, ini_name=None):
        self.__config = ConfigParser()
        self.__ini_path = self.__set_ini_path(ini_path, ini_name)
        self.__section_names = list(config_instance.__dict__.keys())
        self.__section_classes = dict(config_instance.__dict__.items())
        self.__section_mappings = {
            x: {z: getattr(y, z) for z in y.__dict__.keys()}
            for x, y in zip(self.__section_classes.keys(), self.__section_classes.values())
        }

    @staticmethod
    def __set_ini_path(ini_path, ini_name):
        if ini_path is None:
            ini_path = getcwd()

        if ini_name is not None:
            ini_name = ini_name.strip()
            if ini_name[0] != "/":
                ini_name = "/" + ini_name
            elif not ini_name.endswith(".ini"):
                ini_name = ini_name + ".ini"
        else:
            ini_name = "/default.ini"

        return ini_path + ini_name

    def read_config(self):
        """ Attempts to read the config specified by ini_path. If the file is not found, a new config is generated using
         default values from the config object.
         After successfully parsing a value in the config, the method will search for the corresponding attribute in the
         config object's section class and change it to the parsed one (if it is of a valid type).
         When handling duplicate sections/options, all but the first instance of the entry is ignored."""

        output_list = []
        error_message_type = "****Error in config: Entry ({}) Invalid type - should be a ({}). " \
                             "Using default value instead."
        error_message_section_missing = "****Error in config: Missing section: ({}). Using default values instead."
        error_message_entry_missing = "****Error in config: Missing entry: ({}). Using default value instead."
        error_duplicate_option = "****Error in config: Multiple options named ({}) in section ({}). " \
                                 "Can not read config until duplicate options are removed."
        error_duplicate_section = "****Error in config: Multiple sections named ({}). " \
                                  "Can not read config until duplicate sections are removed."

        type_error_mappings = {  # for error messages involving invalid types.
            int: "Number",
            str: "String",
            list: "List eg - val1,val2,val3,etc",
            dict: "Dict eg - key:value,key2:value,key3:value,etc"
        }

        if not path.exists(self.__ini_path):
            output_list.append("Ini file did not exist in the specified location.")
            self.flush_config()
            output_list.append("A new ini file was created with default values.")
            return output_list

        try:
            self.__config.read(self.__ini_path)
        except DuplicateOptionError as e:
            output_list.append(error_duplicate_option.format(e.option, e.section))
        except DuplicateSectionError as e:
            output_list.append(error_duplicate_section.format(e.section))

        if len(output_list) != 0:  # Can't continue if any of the above is true. # ToDo: find a way to make it work
            return output_list

        for section, section_options in self.__section_mappings.items():
            if not self.__config.has_section(section):  # The user config is missing the section. Skip it.
                output_list.append(error_message_section_missing.format(section))
                continue
            for option_name, option_value in self.__section_mappings[section].items():
                if not self.__config.has_option(section, option_name):  # The user config is missing the option. Skip.
                    output_list.append(error_message_entry_missing.format(option_name))
                    continue
                required_type = type(option_value)  # What type is the object expecting the attribute to have?
                user_option_value = self.__config.get(section, option_name)
                try:
                    if required_type is dict or required_type is list:  # Try to handle list/dict options
                        if ',' in user_option_value and ':' in user_option_value:
                            user_option_value = dict(x.split(":") for x in user_option_value.split(','))
                        elif ',' in user_option_value and ':' not in user_option_value:
                            user_option_value = list(user_option_value.split(','))
                    user_option_value = required_type(user_option_value)  # Try to convert user option to correct value
                    setattr(self.__section_classes[section], option_name, user_option_value)
                except ValueError:
                    output_list.append(error_message_type.format(
                        option_name, type_error_mappings[required_type], option_value)
                    )

        if len(output_list) != 0:
            output_list.append("\nThere were errors while reading some of the config options.")
            output_list.append("A new config file will now be generated (with correctly read values preserved) using "
                               "default values for the options which failed to be read.")
            self.flush_config()
            return output_list

    def flush_config(self):  # ToDo: Add some exception handling to this
        """ Takes all of the settings in the object representing the config and creates an ini with them. """
        with open(self.__ini_path, "w") as ini_file:
            for section in self.__section_names:
                if not self.__config.has_section(section):
                    self.__config.add_section(section)
                for option_name, option_value in self.__section_mappings[section].items():
                    if type(option_value) is dict:
                        new_value = ""
                        for key, value in option_value.items():
                            new_value += "{}:{},".format(key, value)
                        option_value = new_value[:-1]  # remove trailing comma. could just use rstrip but with the
                    if type(option_value) is list:  # way this is written, there always will be a leading comma.
                        new_value = ""
                        for value in option_value:
                            new_value += "{},".format(value)
                        option_value = new_value[:-1]
                    self.__config.set(section, option_name, str(option_value))
            self.__config.write(ini_file)
