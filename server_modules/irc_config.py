from configparser import ConfigParser
from os import getcwd, path


class IRCConfig:
    """ Represent the IRC Config file. On instantiation, it is all automatically set up. """
    def __init__(self):
        self.ServerSettings = self.__ServerSettings()
        self.MaintenanceSettings = self.__MaintenanceSettings()
        self.UserSettings = self.__UserSettings()
        self.__CrowConfigParser = self.__CrowConfigParsingUtils(
            [self.ServerSettings, self.MaintenanceSettings, self.UserSettings]
        )
        self.__CrowConfigParser.read_config()

    class __ServerSettings:
        def __init__(self):
            self.Port = 6667
            self.Interface = "127.0.0.1"
            self.PingInterval = 3
            self.ServerName = "Crow IRC"
            self.ServerDescription = "WIP IRC Server implementation w/ Twisted."
            self.ServerWelcome = "Welcome to Crow IRC"
            self.mapping = {
                "Port": self.Port, "Interface": self.Interface,
                "PingInterval": self.PingInterval, "ServerName": self.ServerName,
                "ServerDescription": self.ServerDescription, "ServerWelcome": self.ServerWelcome
            }

    class __MaintenanceSettings:
        def __init__(self):
            self.RateLimitClearInterval = 5
            self.FlushInterval = 1
            self.ChannelScanInterval = 1
            self.ChannelUltimatum = 7
            self.mapping = {"RateLimitClearInterval": self.RateLimitClearInterval, "FlushInterval": self.FlushInterval,
                              "ChannelScanInterval": self.ChannelScanInterval, "ChannelUltimatum": self.ChannelUltimatum}

    class __UserSettings:
        def __init__(self):
            self.MaxUsernameLength = 35
            self.MaxNicknameLength = 35
            self.MaxClients = 5
            self.Operators = {"Admin": "Password", "Admin2": "Password2"}
            self.mapping = {"MaxUsernameLength": self.MaxUsernameLength, "MaxNicknameLength": self.MaxNicknameLength,
                              "MaxClients": self.MaxClients, "Operators": self.Operators}

    class __CrowConfigParsingUtils:
        """ Parse the actual config, instantiate the IRCConfig object """
        def __init__(self, settings_classes):
            self.config = ConfigParser()
            self.crow_path = getcwd().split("/bin")[0]
            self.config_path = self.crow_path + "/crow.ini"
            self.settings_classes = settings_classes
            self.section_names = [type(x).__name__.split("__")[1] for x in self.settings_classes]
            self.section_associations = {x: y for x, y in zip(self.section_names, self.settings_classes)}
            self.section_mappings = {x: y.mapping for x, y in zip(self.section_names, self.settings_classes)}

        def config_exists(self):
            return path.exists(self.config_path)

        def read_config(self):
            error_message_entry = "****Error in config: Invalid entry: {}." \
                                  "\nReason: {}" \
                                  "\nUsing default value for this entry instead.****"

            error_message_section_missing = "****Error in config: Missing section: {}." \
                                            "\nUsing default values for this section instead.****"

            error_message_entry_missing = "****Error in config: Missing entry: {}." \
                                          "\nUsing default value for this entry instead.\n****"

            # Thank god these loops are only run once lol
            self.config.read(self.config_path)
            for section, section_options in self.section_mappings.items():
                for option_name, option_value in self.section_mappings[section].items():
                    if section not in self.config.keys():
                        print(error_message_section_missing.format(section))
                    else:
                        if option_name not in self.config[section]:
                            print(error_message_entry_missing.format(option_name))
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
                                print(error_message_entry.format(
                                    option_name, "Option is of an invalid type. Should be: {}".format(option_type)
                                ))
            #  Save the config now

        def create_config(self):
            #  This needs to be rewritten as well
            errors = None
            with open(self.config_path, 'w') as crow_ini:
                self.config.add_section("ServerSettings")
                self.config.set("ServerSettings", "Port", str(self.serversettings["port"]))
                self.config.set("ServerSettings", "Interface", str(self.serversettings["interface"]))
                self.config.set("ServerSettings", "PingInterval", str(self.serversettings["pinginterval"]))
                self.config.set("ServerSettings", "ServerName", str(self.serversettings["servername"]))
                self.config.set("ServerSettings", "ServerDescription", str(self.serversettings["serverdescription"]))
                self.config.set("ServerSettings", "ServerWelcome", str(self.serversettings["serverwelcome"]))
                self.config.add_section("MaintenanceSettings")
                self.config.set("MaintenanceSettings", "RateLimitClearInterval", str(self.maintenancesettings["ratelimitclearinterval"]))
                self.config.set("MaintenanceSettings", "FlushInterval", str(self.maintenancesettings["flushinterval"]))
                self.config.set("MaintenanceSettings", "ChannelScanInterval", str(self.maintenancesettings["channelscaninterval"]))
                self.config.set("MaintenanceSettings", "ChannelUltimatum", str(self.maintenancesettings["channelultimatum"]))
                self.config.add_section("UserSettings")
                self.config.set("UserSettings", "MaxUsernameLength", str(self.usersettings["maxusernamelength"]))
                self.config.set("UserSettings", "MaxNicknameLength", str(self.usersettings["maxnicknamelength"]))
                self.config.set("UserSettings", "MaxClients", str(self.usersettings["maxclients"]))
                self.config.set("UserSettings", "Operators", str(self.usersettings["operators"]))
                try:
                    self.config.write(crow_ini)
                except Exception as e:
                    errors = str(e)
            return errors


