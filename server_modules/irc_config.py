from configparser import ConfigParser
from os import getcwd, path


class IRCConfig:
    def __init__(self):
        self.ServerSettings = None
        self.ChannelSettings = None
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
                "Port": int(self._crow_config['ServerSettings']['Port'])
            }
            self.ChannelSettings = {
                "MaxChannels": int(self._crow_config['ChannelSettings']['Max_Channels']),
                "MaxConnected": int(self._crow_config['ChannelSettings']['Max_Connected'])
            }
            self.NicknameSettings = {
                "ReservedNicknames": [n for n in str(self._crow_config['NicknameSettings']['Reserved_Nicknames']).split(',')],
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
            self._crow_config.add_section("ChannelSettings")
            self._crow_config.set("ChannelSettings", "Max_Channels", "35")
            self._crow_config.set("ChannelSettings", "Max_Connected", "50")
            self._crow_config.add_section("NicknameSettings")
            self._crow_config.set("NicknameSettings", "Reserved_Nicknames", "Admin,Owner")
            self._crow_config.set("NicknameSettings", "Max_Length", "35")
            try:
                self._crow_config.write(crow_ini)
            except Exception as e:
                errors = str(e)
        return errors
