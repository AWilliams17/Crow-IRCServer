from util_packages.sentry.sentry_config import *


class ValidatorTest(SentryCriteria):
    def criteria(self, value):
        if value != "Test":
            return False

    @property
    def criteria_description(self):
        return "Not valid."


class IRCConfig(SentryConfig):
    class TestSection(SentrySection):
        TestOption = SentryOption("Default", ValidatorTest())

"""
class IRCConfig(SentryConfig):
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
        Operators = SentryOption({"Admin": "Password", "Admin2": "Password2"})  # lol
"""