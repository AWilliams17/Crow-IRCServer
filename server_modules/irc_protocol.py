from twisted.words.protocols.irc import IRC, protocol
from server_modules.irc_channel import IRCChannel


class IRCProtocol(IRC):
    def __init__(self, users, channels):
        self.users = users
        self.channels = channels
        self.user_name = None

    def connectionMade(self):
        server_name = "Test-IRCServer"  # Place Holder!
        self.sendLine("You are now connected to %s" % server_name)  # ToDo: Implement the server_name properly.

    def connectionLost(self, reason=protocol.connectionDone):
        pass

    def handleCommand(self, command, prefix, params):
        pass

    def irc_unknown(self, prefix, command, params):
        raise NotImplementedError(command, prefix, params)
