from configparser import ConfigParser
from os import getcwd, path
# ToDo: Make Max Clients work


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
                "ServerName": str(self._crow_config['ServerSettings']['ServerName'])
            }
            self.UserSettings = {
                "MaxLength": int(self._crow_config['UserSettings']['Max_Length']),
                "MaxClients": int(self._crow_config['UserSettings']['Max_Clients'])
            }
            self.NicknameSettings = {
                "MaxLength": int(self._crow_config['NicknameSettings']['Max_Length'])
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
            self._crow_config.add_section("NicknameSettings")
            self._crow_config.set("NicknameSettings", "Max_Length", "35")
            self._crow_config.add_section("UserSettings")
            self._crow_config.set("UserSettings", "Max_Length", "35")
            self._crow_config.set("UserSettings", "Max_Clients", "5")
            try:
                self._crow_config.write(crow_ini)
            except Exception as e:
                errors = str(e)
        return errors
