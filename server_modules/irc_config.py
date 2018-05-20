from configparser import ConfigParser
from os import getcwd, path


class IRCConfig:
    def __init__(self):
        self.ServerSettings = None
        self.UserSettings = None
        self.NicknameSettings = None
        self._crow_config = ConfigParser()
        self._crow_path = getcwd().split("/bin")[0]
        self._config_path = self._crow_path + "/crow.ini"

    def config_exists(self):
        return path.exists(self._config_path)

    def read_config(self):
        self._crow_config.read(self._config_path)
        errors = None
        try:
            self.ServerSettings = {
                "Port": int(self._crow_config['ServerSettings']['Port']),
                "ServerName": str(self._crow_config['ServerSettings']['ServerName']),
                "ServerDescription": str(self._crow_config['ServerSettings']['ServerDescription'])
            }
            self.UserSettings = {
                "MaxLength": int(self._crow_config['UserSettings']['MaxLength']),
                "MaxClients": int(self._crow_config['UserSettings']['MaxClients']),
            }
            self.NicknameSettings = {
                "MaxLength": int(self._crow_config['NicknameSettings']['MaxLength'])
            }
        except Exception as e:
            errors = str(e)
        return errors

    def create_config(self):
        errors = None
        with open(self._config_path, 'w') as crow_ini:
            self._crow_config.add_section("ServerSettings")
            self._crow_config.set("ServerSettings", "Port", "6667")
            self._crow_config.set("ServerSettings", "ServerName", "Crow IRC")
            self._crow_config.set("ServerSettings", "ServerDescription", "WIP IRC Server implementation w/ Twisted.")
            self._crow_config.add_section("NicknameSettings")
            self._crow_config.set("NicknameSettings", "MaxLength", "35")
            self._crow_config.add_section("UserSettings")
            self._crow_config.set("UserSettings", "MaxLength", "35")
            self._crow_config.set("UserSettings", "MaxClients", "5")
            try:
                self._crow_config.write(crow_ini)
            except Exception as e:
                errors = str(e)
        return errors
