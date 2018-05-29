from util_packages.sentry.sentry_config import *


class IRCConfig(SentryConfig):
    def __init__(self):
        self.ServerSettings = self.__ServerSettingsSection("ServerSettings")
        self.MaintenanceSettings = self.__MaintenanceSettingsSection("MaintenanceSettings")
        self.UserSettings = self.__UserSettingsSection("UserSettings")

    class __ServerSettingsSection(SentrySection):
        Port = SentryOption(6667, lambda x: x != 0, "Port can not be zero.")

    class __MaintenanceSettingsSection(SentrySection):
        FlushInterval = SentryOption(1, lambda x: x != 0, "Value must not be 0 or server details will never be saved.")

    class __UserSettingsSection(SentrySection):
        MaxUsernameLength = SentryOption(35, lambda x: x >= 5, "Usernames can not be less than 5.")


"""
    class __ServerSettings(ConfigReaperSection):
        Port = ConfigReaperOption(6667)
        Interface = ConfigReaperOption("127.0.0.1")
        PingInterval = ConfigReaperOption(3)
        ServerName = ConfigReaperOption("Crow IRC")
        ServerDescription = ConfigReaperOption("WIP IRC Server implementation w/ Twisted.")
        ServerWelcome = ConfigReaperOption("Welcome to Crow IRC")

    class __MaintenanceSettings(ConfigReaperSection):
        RateLimitClearInterval = ConfigReaperOption(5)
        FlushInterval = ConfigReaperOption(1)
        ChannelScanInterval = ConfigReaperOption(1)
        ChannelUltimatum = ConfigReaperOption(7)

    class __UserSettings(ConfigReaperSection):
        MaxUsernameLength = ConfigReaperOption(35)
        MaxNicknameLength = ConfigReaperOption(35)
        MaxClients = ConfigReaperOption(5)
        Operators = ConfigReaperOption({"Admin": "Password", "Admin2": "Password2"})  # lol
"""