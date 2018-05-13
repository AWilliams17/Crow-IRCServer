from twisted.words.protocols.irc import IRC, protocol, IRCBadMessage
from server_modules.irc_channel import IRCChannel


class IRCProtocol(IRC):
    def __init__(self, users, channels):
        self.users = users
        self.channels = channels
        self.nickname = None
        self.username = None

    def connectionMade(self):
        server_name = "Test-IRCServer"  # Place Holder!
        self.sendLine("You are now connected to %s" % server_name)  # ToDo: Implement the server_name properly.

    def connectionLost(self, reason=protocol.connectionDone):
        pass

    def irc_unknown(self, prefix, command, params):
        self.sendLine("Error: Unknown command: {}{}".format(command, params))

    def irc_JOIN(self, prefix, params):
        channel = params[0]
        user = "{}!{}@{}".format(
            self.users[self.username][2],
            self.users[self.username][3],
            self.users[self.username][4]
        )
        if channel not in self.channels:
            self.channels[channel] = IRCChannel(channel)

        self.topic(self.username, self.channels[channel].channel_name, topic="Test")
        self.join(user, channel)
        self.channels[channel].users.append(self.users[self.username])
        self.channels[channel].usernames.append(self.users[self.username][1])
        self.channels[channel].nicknames.append(self.users[self.username][2])

        self.names(self.username, self.channels[channel].channel_name, self.channels[channel].nicknames)

    def irc_NICK(self, prefix, params):
        self.nickname = params[0]

    def irc_USER(self, prefix, params):
        self.username = params[0]
        ident = params[1]
        hostmask = params[2]
        self.users[self.username] = [self, self.username, self.nickname, ident, hostmask]

