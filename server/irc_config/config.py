from sentry.sentry_config import *
from sentry.sentry_validators import *
from server.irc_config.validators import *
from server.irc_config.option_descriptions import *


class IRCConfig(SentryConfig):
    """ Represents the server configuration file. """
    class ServerSettings(SentrySection):
        Port = SentryOption(
            default=[6665, 6666, 6667, 8000, 8001, 8002],
            criteria=PortsCriteria,
            description=PortsDescription
        )
        Interface = SentryOption(
            default="127.0.0.1",
            criteria=None,
            description=InterfaceDescription
        )
        PingInterval = SentryOption(
            default=3,
            criteria=IntRequired,
            description=PingIntervalDescription
        )
        ServerName = SentryOption(
            default="Crow IRC",
            criteria=None,
            description=ServerNameDescription
        )
        ServerDescription = SentryOption(
            default="WIP IRC Server implementation w/ Twisted.",
            criteria=None,
            description=ServerDescriptionDescription
        )
        ServerWelcome = SentryOption(
            default="Welcome to Crow IRC",
            criteria=None,
            description=ServerWelcomeDescription
        )

    class MaintenanceSettings(SentrySection):
        RateLimitClearInterval = SentryOption(
            default=5,
            criteria=IntRequired,
            description=RateLimitClearIntervalDescription
        )
        FlushInterval = SentryOption(
            default=1,
            criteria=IntRequired,
            description=FlushIntervalDescription
        )
        ChannelScanInterval = SentryOption(
            default=1,
            criteria=IntRequired,
            description=ChannelScanIntervalDescription
        )
        ChannelUltimatum = SentryOption(
            default=7,
            criteria=IntRequired,
            description=ChannelUltimatumDescription
        )

    class UserSettings(SentrySection):
        MaxUsernameLength = SentryOption(
            default=35,
            criteria=[IntRequired, MaxUsernameLengthCriteria],
            description=MaxUsernameLengthDescription
        )
        MaxNicknameLength = SentryOption(
            default=35,
            criteria=[IntRequired, MaxNicknameLengthCriteria],
            description=MaxNicknameLengthDescription
        )
        MaxClients = SentryOption(
            default=5,
            criteria=[IntRequired, MaxClientsCriteria],
            description=MaxClientsDescription
        )
        Operators = SentryOption(
            default={"Admin": "Password", "Admin2": "Password2"},
            criteria=None,
            description=OperatorsDescription
        )

    class SSLSettings(SentrySection):
        SSLEnabled = SentryOption(
            default=False,
            criteria=BoolRequired,
            description=SSLEnabledDescription
        )
        SSLPorts = SentryOption(
            default=[6697, 7000, 7070],
            criteria=SSLPortsCriteria,
            description=SSLPortsDescription
        )
        SSLOnly = SentryOption(
            default=False,
            criteria=BoolRequired,
            description=SSLOnlyDescription
        )
        SSLKeyPath = SentryOption(
            default=None,
            criteria=[StringRequired, SSLKeyPathCriteria],
            description=SSLKeyPathDescription
        )
        SSLCertPath = SentryOption(
            default=None,
            criteria=[StringRequired, SSLCertPathCriteria],
            description=SSLCertPathDescription
        )
