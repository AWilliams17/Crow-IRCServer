from utils.sentry.sentry_config import *
from utils.sentry.sentry_type_converters import *
from server.irc_config.validators import *
from server.irc_config.option_descriptions import *


class IRCConfig(SentryConfig):
    """ Represents the server configuration file. """
    class ServerSettings(SentrySection):
        Port = SentryOption(6667, IntConverter, PortDescription)
        Interface = SentryOption("127.0.0.1", description=InterfaceDescription)
        PingInterval = SentryOption(3, IntConverter, PingIntervalDescription)
        ServerName = SentryOption("Crow IRC", description=ServerNameDescription)
        ServerDescription = SentryOption("WIP IRC Server implementation w/ Twisted.", description=ServerNameDescription)
        ServerWelcome = SentryOption("Welcome to Crow IRC", description=ServerWelcomeDescription)

    class MaintenanceSettings(SentrySection):
        RateLimitClearInterval = SentryOption(5, IntConverter, RateLimitClearIntervalDescription)
        FlushInterval = SentryOption(1, IntConverter, FlushIntervalDescription)
        ChannelScanInterval = SentryOption(1, IntConverter, ChannelScanIntervalDescription)
        ChannelUltimatum = SentryOption(7, IntConverter, ChannelUltimatumDescription)

    class UserSettings(SentrySection):
        MaxUsernameLength = SentryOption(35, [IntConverter, MaxUsernameLengthCriteria], MaxUsernameLengthDescription)
        MaxNicknameLength = SentryOption(35, [IntConverter, MaxNicknameLengthCriteria], MaxNicknameLengthDescription)
        MaxClients = SentryOption(5, [IntConverter, MaxClientsCriteria], MaxClientsDescription)
        Operators = SentryOption({"Admin": "Password", "Admin2": "Password2"}, DictConverter, OperatorsDescription)
        # lol ^
