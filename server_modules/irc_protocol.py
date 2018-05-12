from twisted.words.protocols.irc import IRC, protocol
from server_modules.irc_channel import IRCChannel


class IRCProtocol(IRC):
    def __init__(self):
        pass

    def connectionMade(self):
        pass

    def connectionLost(self, reason=protocol.connectionDone):
        pass

    def handleCommand(self, command, prefix, params):
        pass

    def join(self, who, where):
        pass


