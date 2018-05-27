from configparser import ConfigParser
from os import path


class ConfigReaper:
    def __init__(self, config_instance, ini_path):
        self.config = ConfigParser()
        self.ini_path = ini_path
        self.section_names = list(config_instance.__dict__.keys())
        self.section_classes = dict(config_instance.__dict__.items())
        self.section_mappings = {
            x: {z: getattr(y, z) for z in y.__dict__.keys()}
            for x, y in zip(self.section_classes.keys(), self.section_classes.values())
        }


        # setattr(self.section_associations[section], option_name, user_defined_option)
        # setattr(section_class, option_name, user_defined_option)

        #section_objects = config_instance.__dict__
        #for section_name, section_class in section_objects.items():
        #    section_mapping = section_objects[section_name].__dict__.items()
        #    for option_name, option_value in section_mapping:
        #        pass

        #self.section_associations = {x: y for x, y in zip(self.section_names, config_instance)}

        """
        self.settings_classes = section_classes
        self.section_names = [type(x).__name__.split("__")[1] for x in self.settings_classes]
        self.section_associations = {x: y for x, y in zip(self.section_names, self.settings_classes)}
        self.section_mappings = {
            x: {z: getattr(y, z) for z in y.__dict__.keys()}
            for x, y in zip(self.section_names, self.settings_classes)
        }
        """

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

        """
        I need to first check if the file passed in ini_file exists or not. If it doesn't, call self.flush_config to
        make one, and then add a message to error_list and return it.
        Otherwise, continue.
        
        Now, if it DOES exist, I need to iterate over all the items in the section mappings, and see if there
        is a corresponding section/option name in the config which got read.
        If there is not a section, just add an error message to the list and continue.
        If there is a section, then go through it and for every option in the section mapping's options list,
        see if there is also a corresponding option in the user config.
        If there is not a corresponding option in the user config, add an error message to the list and continue.
        If there is, then:
            1: Verify it is not corrupt or misformatted
            2: Try to turn it into the same type as the original option
            3: Call setattr on the section class and update the option name
        If any of those checks fail, then add an error message to the list and continue.
        At the end of all of this, if there were any errors, re-flush the config to fix the config file
        and then return the error list.
        Otherwise, return None.
        """



        """
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
        return 
        """

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