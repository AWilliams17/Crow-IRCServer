from twisted.internet.protocol import Factory
from server_modules.irc_protocol import IRCProtocol


class ChatServer(Factory):

    def __init__(self):
        self.users = {}  # maps user names to Chat instances
        self.rooms = {}  # maps rooms to Chat instances

    def buildProtocol(self, address):
        return IRCProtocol(self.users, self.rooms)
