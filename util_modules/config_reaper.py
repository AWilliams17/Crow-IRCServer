from configparser import ConfigParser
from os import path


class ConfigReaper:
    def __init__(self, section_classes, ini_path):
        self.config = ConfigParser()
        self.ini_path = ini_path
        self.settings_classes = section_classes
        self.section_names = [type(x).__name__.split("__")[1] for x in self.settings_classes]
        self.section_associations = {x: y for x, y in zip(self.section_names, self.settings_classes)}
        self.section_mappings = {
            x: {z: getattr(y, z) for z in y.__dict__.keys()}
            for x, y in zip(self.section_names, self.settings_classes)
        }

    def config_exists(self):
        return path.exists(self.ini_path)

    def read_config(self):
        error_list = []
        error_message_entry = "****Error in config: Invalid entry: {}." \
                              "\nReason: {}" \
                              "\nUsing default value for this entry instead.****\n"

        error_message_section_missing = "****Error in config: Missing section: {}." \
                                        "\nUsing default values for this section instead.****\n"

        error_message_entry_missing = "****Error in config: Missing entry: {}." \
                                      "\nUsing default value for this entry instead.\n****"

        type_error_mappings = {  # for error messages involving invalid types.
            int: "Number",
            str: "String",
            list: "List eg - val1,val2,val3,etc",
            dict: "Dict eg - key:value,key2:value,key3:value,etc"
        }

        # Thank god these loops are only run once lol
        if not self.config_exists():
            raise FileNotFoundError("Configuration file was not found.")
        self.config.read(self.ini_path)
        for section, section_options in self.section_mappings.items():
            if section not in self.config.keys():
                error_list.append(error_message_section_missing.format(section))
            else:
                for option_name, option_value in self.section_mappings[section].items():
                    if option_name not in self.config[section]:
                        error_list.append(error_message_entry_missing.format(option_name))
                    else:
                        user_defined_option = self.config[section][option_name]
                        option_type = type(option_value)
                        try:
                            if option_type is dict:
                                user_defined_option = dict(x.split(":") for x in user_defined_option.split(','))
                            if option_type is list:
                                user_defined_option = [x.split(" ") for x in user_defined_option.split(',')]
                            user_defined_option = option_type(user_defined_option)
                            setattr(self.section_associations[section], option_name, user_defined_option)
                        except ValueError:
                            error_list.append(error_message_entry.format(
                                option_name, "Invalid type. Should be: {}".format(type_error_mappings[option_type])
                            ))
        if len(error_list) != 0:
            return error_list
        return None

    def flush_config(self):
        with open(self.ini_path, "w") as ini_file:
            for section in self.section_names:
                self.config.add_section(section)
                for option_name, option_value in self.section_mappings[section].items():
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
                    self.config.set(section, option_name, str(option_value))
            self.config.write(ini_file)