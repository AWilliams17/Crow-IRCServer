from utils.sentry.sentry_config import *
from utils.sentry.sentry_type_converters import *
from server.irc_config.validators import *
from server.irc_config.option_descriptions import *


class IRCConfig(SentryConfig):
    """ Represents the server configuration file. """
    class ServerSettings(SentrySection):
        Port = SentryOption(6667)
        Interface = SentryOption("127.0.0.1")
        PingInterval = SentryOption(3)
        ServerName = SentryOption("Crow IRC")
        ServerDescription = SentryOption("WIP IRC Server implementation w/ Twisted.")
        ServerWelcome = SentryOption("Welcome to Crow IRC")

    class MaintenanceSettings(SentrySection):
        RateLimitClearInterval = SentryOption(5)
        FlushInterval = SentryOption(1)
        ChannelScanInterval = SentryOption(1)
        ChannelUltimatum = SentryOption(7)

    class UserSettings(SentrySection):
        MaxUsernameLength = SentryOption(35)
        MaxNicknameLength = SentryOption(35)
        MaxClients = SentryOption(5)
        Operators = SentryOption({"Admin": "Password", "Admin2": "Password2"})
