from twisted.internet.protocol import Factory
from server_modules.irc_protocol import IRCProtocol


class ChatServer(Factory):
    def __init__(self):
        pass

    def buildProtocol(self, addr):
        pass
