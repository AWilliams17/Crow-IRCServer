from utils.sentry.sentry_config import *
from utils.sentry.sentry_type_converters import *


class IRCConfig(SentryConfig):
    class ServerSettings(SentrySection):
        Port = SentryOption(6667, IntConverter)
        Interface = SentryOption("127.0.0.1")
        PingInterval = SentryOption(3, IntConverter)
        ServerName = SentryOption("Crow IRC")
        ServerDescription = SentryOption("WIP IRC Server implementation w/ Twisted.")
        ServerWelcome = SentryOption("Welcome to Crow IRC")

    class MaintenanceSettings(SentrySection):
        RateLimitClearInterval = SentryOption(5, IntConverter)
        FlushInterval = SentryOption(1, IntConverter)
        ChannelScanInterval = SentryOption(1, IntConverter)
        ChannelUltimatum = SentryOption(7, IntConverter)

    class UserSettings(SentrySection):
        MaxUsernameLength = SentryOption(35, IntConverter)
        MaxNicknameLength = SentryOption(35, IntConverter)
        MaxClients = SentryOption(5, IntConverter)
        Operators = SentryOption({"Admin": "Password", "Admin2": "Password2"}, DictConverter)  # lol
