from twisted.internet.protocol import Factory
from server_modules.irc_protocol import IRCProtocol


class ChatServer(Factory):
    def __init__(self):
        self.users = {}
        self.channels = {}

    def buildProtocol(self, addr):
        return IRCProtocol(self.users, self.channels)
