#  ToDo: This all needs to be more thoroughly tested.
from configparser import ConfigParser
from os import path, getcwd


class ConfigReaper:
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
        error_list = []
        error_tail = "\nUsing default value ({}) for this entry instead."
        error_tail_section = "\nUsing default values for this section instead."
        error_message_type = "****Error in config: Entry {} is of an invalid type - should be a {}." + error_tail
        error_message_section_missing = "****Error in config: Missing section: {}." + error_tail_section
        error_message_entry_missing = "****Error in config: Missing entry: {}." + error_tail

        type_error_mappings = {  # for error messages involving invalid types.
            int: "Number",
            str: "String",
            list: "List eg - val1,val2,val3,etc",
            dict: "Dict eg - key:value,key2:value,key3:value,etc"
        }

        if not path.exists(self.__ini_path):
            error_list.append("Ini file did not exist in the specified location.")
            self.flush_config()
            error_list.append("A new ini file was created with default values.")
            return error_list
        self.__config.read(self.__ini_path)
        for section, section_options in self.__section_mappings.items():
            if not self.__config.has_section(section):
                error_list.append(error_message_section_missing.format(section))
                continue
            for option_name, option_value in self.__section_mappings[section].items():
                if not self.__config.has_option(section, option_name):
                    error_list.append(error_message_entry_missing.format(option_name))
                required_type = type(option_value)
                user_option_value = self.__config.get(section, option_name)
                try:
                    if required_type is dict or required_type is list:
                        if ',' in user_option_value and ':' in user_option_value:
                            user_option_value = dict(x.split(":") for x in user_option_value.split(','))
                        elif ',' in user_option_value and ':' not in user_option_value:
                            user_option_value = list(user_option_value.split(','))
                    user_option_value = required_type(user_option_value)
                    setattr(self.__section_classes[section], option_name, user_option_value)
                except ValueError:
                    error_list.append(error_message_type.format(
                        option_name, type_error_mappings[required_type], option_value)
                    )
        if len(error_list) != 0:
            error_list.append("\nThere were errors while reading some of the config options.")
            error_list.append("A new config file will now be generated (with correctly read values preserved) using "
                              "default values for the options which failed to be read.")
            self.flush_config()
            return error_list

    def flush_config(self):
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
