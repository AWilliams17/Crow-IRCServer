from twisted.words.protocols.irc import IRC, protocol
from twisted.internet.error import ConnectionLost
from server_modules.irc_channel import IRCChannel, QuitReason
from server_modules.irc_user import IRCUser
# ToDo: Implement CAP
# ToDo: Implement WHOIS
# ToDo: Implement MODE
# ToDo: Implement PING/PONG (since I guess it doesn't work?)


class IRCProtocol(IRC):
    def __init__(self, users, channels, config):
        self.users = users
        self.channels = channels
        self.config = config

    def connectionMade(self):
        server_name = self.config.ServerSettings['ServerName']
        max_nick_length = self.config.NicknameSettings['MaxLength']
        max_user_length = self.config.UserSettings['MaxLength']
        self.sendLine("You are now connected to %s" % server_name)
        self.users[self] = IRCUser(self, None, None, None, self.transport.getPeer().host,
                                   None, [], 0, max_nick_length, max_user_length)

    def connectionLost(self, reason=protocol.connectionDone):
        if self in self.users:
            for channel in self.users[self].channels:
                quit_reason = QuitReason.UNSPECIFIED
                if reason.type == ConnectionLost:
                    quit_reason = QuitReason.TIMEOUT
                channel.remove_user(self.users[self], reason=quit_reason)
            del self.users[self]

    def irc_unknown(self, prefix, command, params):
        self.sendLine("Error: Unknown command: '{} {}'".format(command, params))

    def irc_JOIN(self, prefix, params):
        if len(params) != 1:
            self.sendLine("Error: maximum/minimum 1 parameter.")
            return

        channel = params[0].lower()
        if channel[0] != "#":
            channel = "#" + channel

        # The channel doesn't exist on the network - create it.
        if channel not in self.channels:
            self.channels[channel] = IRCChannel(channel)

        # Map this protocol instance to the channel's current clients,
        # and then add this channel to the list of channels the user is connected to.
        results = self.channels[channel].add_user(self.users[self])
        if results is not None:
            self.sendLine(results)

    def irc_QUIT(self, prefix, params):
        if self in self.users:
            for channel in self.users[self].channels:
                channel.remove_user(self.users[self], reason=QuitReason.DISCONNECTED)
            del self.users[self]

    def irc_PART(self, prefix, params):
        channel = params[0]
        self.channels[channel].remove_user(self.users[self], reason=QuitReason.LEFT)

    def irc_PRIVMSG(self, prefix, params):
        param_count = len(params)

        if param_count < 2:
            self.sendLine("Error: Not enough parameters (2 required)")
        elif param_count > 2:
            self.sendLine("Error: Too many parameters (max: 2)")
        else:
            results = self.users[self].send_msg(params[0], params[1])
            if results is not None:
                self.sendLine(results)

    def irc_NICK(self, prefix, params):
        attempted_nickname = params[0]

        results = self.users[self].set_nickname(attempted_nickname)
        if results is not None:
            self.sendLine(results)

    def irc_USER(self, prefix, params):
        username = params[0]
        realname = params[3]

        results = self.users[self].set_username(username, realname)
        if results is not None:  # Their username is invalid. Boot them.
            self.sendLine(results)
            self.transport.loseConnection()

    def irc_CAP(self, prefix, params):
        pass

    def irc_WHO(self, prefix, params):
        if params[0] in self.channels:
            results = self.channels[params[0]].who(
                self.users[self],
                self.users[self].hostmask,
                self.transport.getHost().host)
            if results is not None:
                self.who(self.users[self].nickname, params[0], results)
                return
        self.sendLine(":{} 315 {} {} :End of /WHO list.".format(
            self.users[self].hostmask,
            self.users[self].nickname,
            params[0])
        )

    def irc_WHOIS(self, prefix, params):
        pass

    def irc_MODE(self, prefix, params):
        pass
