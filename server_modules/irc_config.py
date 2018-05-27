# from util_modules.config_reaper import *


class IRCConfig:
    def __init__(self):
        self.ServerSettings = self.__ServerSettings()
        self.MaintenanceSettings = self.__MaintenanceSettings()
        self.UserSettings = self.__UserSettings()

    class __ServerSettings:
        def __init__(self):
            self.Port = 6667
            self.Interface = "127.0.0.1"
            self.PingInterval = 3
            self.ServerName = "Crow IRC"
            self.ServerDescription = "WIP IRC Server implementation w/ Twisted."
            self.ServerWelcome = "Welcome to Crow IRC"

    class __MaintenanceSettings:
        def __init__(self):
            self.RateLimitClearInterval = 5
            self.FlushInterval = 1
            self.ChannelScanInterval = 1
            self.ChannelUltimatum = 7

    class __UserSettings:
        def __init__(self):
            self.MaxUsernameLength = 35
            self.MaxNicknameLength = 35
            self.MaxClients = 5
            self.Operators = {"Admin": "Password", "Admin2": "Password2"}
