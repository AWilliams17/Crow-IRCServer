from twisted.words.protocols.irc import IRC, protocol
from twisted.internet.error import ConnectionLost
from server_modules.irc_channel import IRCChannel, QuitReason
from server_modules.irc_user import IRCUser
# ToDo: Implement CAP
# ToDo: Implement WHO
# ToDo: Implement WHOIS
# ToDo: Implement MODE
# ToDo: Are ping/pongs even working?


class IRCProtocol(IRC):
    def __init__(self, users, channels, config):
        self.users = users
        self.channels = channels
        self.config = config

    def connectionMade(self):
        server_name = "Test-IRCServer"  # Place Holder!
        self.sendLine("You are now connected to %s" % server_name)  # ToDo: Implement the server_name properly.
        self.users[self] = IRCUser(self, None, None, None, self.transport.getPeer().host, None, [], 0)

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
        # ToDo: Add too many channels message along with config option for it
        if channel not in self.channels:
            self.channels[channel] = IRCChannel(channel)

        # Map this protocol instance to the channel's current clients,
        # and then add this channel to the list of channels the user is connected to.
        self.channels[channel].add_user(self.users[self])

    def irc_QUIT(self, prefix, params):
        if self in self.users:
            for channel in self.users[self].channels:
                channel.remove_user(self.users[self], reason=QuitReason.DISCONNECTED)
            del self.users[self]

    def irc_PART(self, prefix, params):
        channel = params[0]
        self.channels[channel].remove_user(self.users[self], reason=QuitReason.LEFT)

    # ToDo: Really there should just be a method for this in irc_user
    # ToDo: Try to refactor this further
    def irc_PRIVMSG(self, prefix, params):
        sender = self.users[self].hostmask
        param_count = len(params)
        destination = None
        message = None
        error = None

        if param_count < 2:
            error = "Error: Not enough parameters.".format(sender)
        else:
            destination = params[0]
            message = params[1]

        if error is None and destination is not None:
            if "*" in destination or "?" in destination:
                error = "Error: Wildcards (? and *) not allowed in destination.".format(sender)
            if error is None and destination[0] == "#":
                if destination not in self.channels:
                    error = "Error: Channel does not exist.".format(sender)
                if error is None and self.users[self] not in self.channels[destination].users:
                    error = "Error: You cannot send messages to a channel you are not in."
            if error is None and destination[0] != "#":
                error = "User not found."
                for i in self.users:
                    destination_user_protocol = self.users.get(i).protocol
                    destination_nickname = self.users.get(i).nickname
                    if self.users[self].protocol != destination_user_protocol and destination_nickname == destination:
                        destination_user_protocol.privmsg(sender, destination, message)
                        return

        if error is not None:
            self.sendLine(error)
            return

        self.channels[destination].broadcast_message(message, sender)

    def irc_NICK(self, prefix, params):
        attempted_nickname = params[0]
        if self.users[self].hostmask is None:
            self.users[self].hostmask = attempted_nickname

        if attempted_nickname == self.users[self].nickname:
            return

        in_use_nicknames = []
        for i in self.users:
            in_use_nicknames.append(self.users[i].nickname)

        # The nickname is taken.
        if attempted_nickname in in_use_nicknames:
            # The user instance has no nickname. This is the case on initial connection.
            if self.users[self].nickname is None:
                # They've had 2 attempts at changing it - Generate one for them.
                if self.users[self].nickattempts != 2:
                    self.sendLine(":{} 433 * {} :Nickname is already in use.".format(
                        self.users[self].host, attempted_nickname)
                    )
                    self.users[self].nickattempts += 1
                else:
                    self.sendLine("Nickname attempts exceeded(2). A random nickname will be generated for you.")
                    self.users[self].rename_to_random_nick(in_use_nicknames)
                    self.sendLine("Your nickname has been set to a random string based on your unique ID.")
            else:
                # The user already has a nick, so just send a line telling them its in use and keep things the same.
                self.sendLine("The nickname {} is already in use.".format(attempted_nickname))
        else:
            try:
                self.users[self].nickname = attempted_nickname
            except ValueError as err:
                self.sendLine(str(err))

    def irc_USER(self, prefix, params):
        try:
            self.users[self].username = params
        except AttributeError as ae:
            self.sendLine(str(ae))
        except ValueError as e:
            self.sendLine(str(e))
            self.transport.loseConnection()

