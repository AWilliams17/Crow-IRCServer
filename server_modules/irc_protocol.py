from twisted.words.protocols.irc import IRC, protocol, IRCBadMessage, IRCClient
from twisted.words.im.ircsupport import irc
from server_modules.irc_channel import IRCChannel


class IRCProtocol(IRC):
    def __init__(self, users, channels):
        self.users = users
        self.channels = channels
        self.username = None
        self.nickname = None

    def connectionMade(self):
        server_name = "Test-IRCServer"  # Place Holder!
        self.sendLine("You are now connected to %s" % server_name)  # ToDo: Implement the server_name properly.

    def connectionLost(self, reason=protocol.connectionDone):
        pass

    def irc_unknown(self, prefix, command, params):
        print(command)
        self.sendLine("Error: Unknown command!")

    def handle_command(self, data):
        prefix, command, params = self.parsemsg(data)
        command = command.upper()
        IRC.handleCommand(self, command, prefix.encode('utf-8'), params)

    def parsemsg(self, s):
        prefix = ''
        trailing = []
        if not s:
            raise IRCBadMessage("Empty line.")
        if s[0] == '/':
            prefix = '/'
            args = s[1:].split()
        else:
            args = s.split()
        command = args.pop(0)
        return prefix, command, args

    def irc_JOIN(self, prefix, params):
        channel = params[0]
        if channel not in self.channels:
            self.channels[channel] = IRCChannel(channel)
            self.channels[channel].users = self.username
            self.topic(self.username, self.channels[channel].channel_name, topic=None)
            self.names(self.username, self.channels[channel].channel_name, self.channels[channel].users)

    def irc_NICK(self, prefix, params):
        self.nickname = params[0]

    def irc_USER(self, prefix, params):
        self.username = params[0]
        self.users[self.username] = [self]

    def irc_CAP(self, prefix, params):
        pass

    def irc_MSG(self, prefix, params):
        pass
