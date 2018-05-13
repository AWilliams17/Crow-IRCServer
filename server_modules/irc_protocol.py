from twisted.words.protocols.irc import IRC, protocol
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

        if channel not in self.channels:  # The channel doesn't exist - create it.
            self.channels[channel] = IRCChannel(channel)

        self.topic(self.username, self.channels[channel].channel_name, topic="Test")  # ToDo: Topics

        self.join(self.users[self.username][5], self.channels[channel].channel_name)

        # Map this protocol instance to the channel's current clients
        self.channels[channel].users.append(self.users[self.username])

        # Send the names in the channel to the connecting user + everyone else
        # ToDo: Refactor these loops.
        channel_nicknames = []
        for i in self.channels[channel].users:
            channel_nicknames.append(i[2])
        for x in self.channels[channel].users:
            x[0].names(x[2], x[0].channels[channel].channel_name, channel_nicknames)

    def irc_PRIVMSG(self, prefix, params):
        destination = params[0]  # Where to send the message
        message = params[1]  # The message
        sender = self.users[self.username][5]

        # if the destination is a channel then echo it to everyone there except the sender
        if destination[0] == "#":
            for x in self.channels[destination].users:
                if x[0] != self:
                    x[0].privmsg(sender, destination, message)
        else:  # otherwise, it is a direct message
            for i in self.users:
                user_protocol = self.users.get(i)[0]
                nick_name = self.users.get(i)[2]
                if user_protocol != self and nick_name == destination:
                    user_protocol.privmsg(sender, destination, message)


    def irc_PART(self, prefix, params):
        pass

    def irc_NICK(self, prefix, params):
        self.nickname = params[0]

    def irc_USER(self, prefix, params):
        self.username = params[0]
        host = params[2]
        realname = params[3]
        hostmask = "{}!{}@{}".format(  # In the format of nickname!username@host
            self.nickname,
            self.username,
            host
        )

        # ToDo: This can be a dictionary.
        self.users[self.username] = [self, self.username, self.nickname, realname, host, hostmask]
