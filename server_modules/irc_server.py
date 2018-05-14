from twisted.internet.protocol import Factory
from server_modules.irc_protocol import IRCProtocol
from collections import OrderedDict


class ChatServer(Factory):
    def __init__(self):
        self.users = OrderedDict()
        self.channels = OrderedDict()

    def buildProtocol(self, addr):
        return IRCProtocol(self.users, self.channels)
