from twisted.words.protocols.irc import IRC, protocol
from twisted.internet.error import ConnectionLost
from server_modules.irc_channel import IRCChannel
from server_modules.irc_user import IRCUser
import random
import string
import re


# ToDo: Jesus Christ DRY
class IRCProtocol(IRC):
    def __init__(self, users, channels):
        self.users = users
        self.channels = channels
        self.nickname = None
        self.username = None
        self.previous = None

    def connectionMade(self):
        server_name = "Test-IRCServer"  # Place Holder!
        self.sendLine("You are now connected to %s" % server_name)  # ToDo: Implement the server_name properly.

        self.users[self] = IRCUser(
            self, self.username, self.nickname, None, self.transport.getHost().host, None, None, 0
        )

    def connectionLost(self, reason=protocol.connectionDone):
        if reason.type is ConnectionLost and self in self.users:
            for channel in self.users[self].channels:
                channel.remove_user(self.users[self])
            del self.users[self]
        # ToDo: Send Timeout message

    def irc_unknown(self, prefix, command, params):
        self.sendLine("Error: Unknown command: {}{}".format(command, params))

    def irc_JOIN(self, prefix, params):
        # self.topic(self.username, self.channels[channel].channel_name, topic="Test")  # ToDo: Topics
        channel = params[0]
        # The channel doesn't exist on the network - create it.
        if channel not in self.channels:
            self.channels[channel] = IRCChannel(channel)

        # Map this protocol instance to the channel's current clients,
        # and then add this channel to the list of channels the user is connected to.
        self.channels[channel].add_user(self.users[self])

    def irc_QUIT(self, prefix, params):
        if self.users[self].protocol in list(self.users.keys()):
            for channel in self.users[self].channels:
                channel.remove_user(self.users[self])
            del self.users[self]

        # ToDo: Send Quit message

    def irc_PART(self, prefix, params):
        channel = params[0]
        self.channels[channel].remove_user(self.users[self])

        # ToDo: Send Leave message

    def irc_PRIVMSG(self, prefix, params):
        destination = params[0]
        message = params[1]
        sender = self.users[self].hostmask

        if destination[0] == "#":
            self.channels[destination].send_message(message, sender)
        else:
            for i in self.users:
                destination_user_protocol = self.users.get(i).protocol
                destination_nickname = self.users.get(i).nickname
                if self.users[self].protocol != destination_user_protocol and destination_nickname == destination:
                    destination_user_protocol.privmsg(sender, destination, message)

    # ToDo: ...Refactor this?
    def irc_NICK(self, prefix, params):
        attempted_nickname = params[0]
        # ToDo: Max_Nick_Length
        if len(attempted_nickname) > 35:
            attempted_nickname = attempted_nickname[:35]
            self.sendLine("Nickname exceeded max char limit(35). It has been trimmed to: {}".format(attempted_nickname))

        # ToDo: Put this in a function. The hostmask is changed multiple times. DRY.
        if self.users[self].hostmask is None:
            self.users[self].hostmask = "{}!{}@{}".format(
                attempted_nickname,
                "*",
                self.users[self].host
            )

        current_nicknames = []
        for i in self.users:
            current_nicknames.append(self.users[i].nickname)

        # The nickname is taken.
        if attempted_nickname in current_nicknames:
            # The user instance has no nickname. This is the case on initial connection.
            if self.users[self].nickname is None:
                # They've had 2 attempts at changing it - Generate one for them.
                if self.users[self].nickattempts >= 2:
                    self.sendLine("Nickname attempts exceeded(2). A random nickname will be generated for you.")
                    protocol_instance_string = str(self.users[self].protocol).replace(" ", "")
                    random_nick = ''.join(random.sample(protocol_instance_string, len(protocol_instance_string)))
                    random_nick_s = re.sub("[.<>_]", "", random_nick[:35])

                    # This is probably (most-definitely) un-needed, but I am paranoid.
                    def validate_nick(nick, current_nicks):
                        if nick in current_nicknames:

                            def generate_junk(amount):
                                return ''.join([
                                    random.choice(
                                        string.ascii_lowercase +
                                        string.ascii_uppercase +
                                        string.digits) for i in range(amount)
                                ])

                            # Re shuffle the string + Add random garbage to it and then re-validate it, keep it under 35
                            nick = (''.join(random.sample(nick, len(nick))) + generate_junk(15))[:35]
                            validate_nick(nick, current_nicks)
                        return nick

                    random_nick_s = validate_nick(random_nick_s, current_nicknames)

                    self.sendLine(":{} NICK {}".format("{}".format(self.users[self].hostmask), random_nick_s))
                    self.sendLine("Your nickname has been set to a random string based off your unique ID.")
                    self.users[self].nickname = random_nick_s
                    self.set_host_mask(random_nick_s, self.users[self].host)

                    self.users[self].nickattempts = 0
                else:
                    self.sendLine(":{} 433 * {} :Nickname is already in use.".format(
                        self.users[self].host, attempted_nickname)
                    )
                    self.users[self].nickattempts += 1
            else:
                # The user already has a nick, so just send a line telling them its in use and keep things the same.
                self.sendLine("The nickname {} is already in use.".format(attempted_nickname))
        else:
            # The user already has connected, therefore he already has a nickname.
            if self.users[self].nickname is not None:
                self.sendLine(":{} NICK {}".format("{}".format(self.users[self].hostmask), attempted_nickname))
                self.users[self].nickname = attempted_nickname
                self.set_host_mask(self.users[self].nickname, self.users[self].host)
                # ToDo: Send notification to users in channel this user has changed his nickname.
            if self.users[self].nickattempts != 0:
                # This is their first connection: they recently tried an invalid nick, so tell them this one is accepted
                self.sendLine(":{} NICK {}".format("{}".format(self.users[self].hostmask), attempted_nickname))
            self.users[self].nickname = attempted_nickname
            self.set_host_mask(self.users[self].nickname, self.users[self].host)

    def irc_USER(self, prefix, params):
        self.users[self].username = params[0]
        self.users[self].realname = params[3]
        self.users[self].channels = []

    def set_host_mask(self, nickname, host):
        username = "*"
        if self.users[self].username is not None:
            username = self.users[self].username
        self.users[self].hostmask = "{}!{}@{}".format(
            nickname,
            username,
            host
        )
