from configparser import ConfigParser
from os import getcwd, path, makedirs


def read_config():
    crow_config = ConfigParser()
    crow_path = getcwd().split("/bin")[0]
    crow_config_path = crow_path + "/crow.ini"

    if not path.exists(crow_config_path):
        return None

    return str(crow_config.read(crow_config_path))


def _create_config(crow_config_path, crow_config):
    with open(crow_config_path, 'w') as crow_ini:
        result = None
        crow_config.add_section("ServerSettings")
        crow_config.set("ServerSettings", "Port", "0")
        crow_config.add_section("ChannelSettings")
        crow_config.set("ChannelSettings", "Max_Channels", "0")
        crow_config.set("ChannelSettings", "Max_Connected", "0")
        crow_config.add_section("NicknameSettings")
        crow_config.set("NicknameSettings", "Reserved_Nicknames", "0")
        crow_config.set("NicknameSettings", "Max_Length", "0")
        try:
            crow_config.write(crow_ini)
        except Exception as e:
            result = str(e)

        return result

