from twisted.words.protocols.irc import IRC, protocol
from twisted.internet.error import ConnectionClosed
from server_modules.irc_channel import IRCChannel
from socket import getfqdn
import random
import string


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
        self.users[self] = {
            "Protocol": self,
            "Username": self.username,
            "Nickname": self.nickname,
            "Realname": None,
            "Host": self.transport.getHost().host,
            "Hostmask": None,
            "Channels": None,
            "Nickattempts": 0,
            "Original_Nickname": None
        }

    def connectionLost(self, reason=protocol.connectionDone):
        """
        # Called when the server loses connection with a client (e.g: server dies or the client times out
        if self.username in self.users and reason is ConnectionClosed:
            for channel in self.users[self.username][6]:
                channel_nicknames = []
                for i in self.channels[channel].users:
                    if i[0] is not self.users[self.username][0]:
                        channel_nicknames.append(i[2])
                for i in self.channels[channel].users:
                    i[0].names(i[2], i[0].channels[channel].channel_name, channel_nicknames)
                self.channels[channel].users.pop(self.channels[channel].users.index(self.users[self.username]))
            del self.users[self.username]
        """
        # ToDo: Send Timeout message
        pass

    def irc_unknown(self, prefix, command, params):
        self.sendLine("Error: Unknown command: {}{}".format(command, params))

    def irc_JOIN(self, prefix, params):
        """
        channel = params[0]

        if channel not in self.channels:  # The channel doesn't exist - create it.
            self.channels[channel] = IRCChannel(channel)

        self.topic(self.username, self.channels[channel].channel_name, topic="Test")  # ToDo: Topics

        self.join(self.users[self.username][5], self.channels[channel].channel_name)

        # Map this protocol instance to the channel's current clients
        # and then add this channel to the list of channels the user is connected to.
        self.channels[channel].users.append(self.users[self.username])
        self.users[self.username][6].append(channel)

        # Send the names in the channel to the connecting user + everyone else
        # ToDo: Refactor these loops.
        channel_nicknames = []
        for i in self.channels[channel].users:
            channel_nicknames.append(i[2])
        for x in self.channels[channel].users:
            x[0].names(x[2], x[0].channels[channel].channel_name, channel_nicknames)
        """
        pass

    def irc_QUIT(self, prefix, params):
        """
        # When a user QUITS the network while in a channel
        if self.username in self.users:
            for channel in self.users[self.username][6]:
                channel_nicknames = []
                for i in self.channels[channel].users:
                    if i[0] is not self.users[self.username][0]:
                        channel_nicknames.append(i[2])
                for i in self.channels[channel].users:
                    i[0].names(i[1], i[0].channels[channel].channel_name, channel_nicknames)
                    if i[0] is self:
                        self.channels[channel].users.pop(self.channels[channel].users.index(self.users[self.username]))
            del self.users[self.username]
        """
        # ToDo: Send Quit message
        pass

    def irc_PART(self, prefix, params):
        """
        # When a user LEAVES a channel
        channel = params[0]
        channel_nicknames = []
        for i in self.channels[channel].users:
            if i[0] is not self.users[self.username][0]:
                channel_nicknames.append(i[2])
        for i in self.channels[channel].users:
            i[0].names(i[2], i[0].channels[channel].channel_name, channel_nicknames)
        self.channels[channel].users.pop(self.channels[channel].users.index(self.users[self.username]))
        """
        # ToDo: Send Leave message
        pass

    def irc_PRIVMSG(self, prefix, params):
        """
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

        #self.sendLine(":{} 432 * {} :Erroneus nickname.".format(
        #    self.transport.getHost().host, "Praetor")
        #)
        #self.sendLine(":{} 433 * {} :Nickname is already in use.".format(
        #    self.transport.getHost().host, "Praetor")
        #)
        #if data == b'NICK Praetor___\r\n':
        #    self.sendLine(":{} NICK {}".format("Praetor!Praetor@127.0.0.1", "Penguin"))



        self.sendLine(":{} 433 * {} :Nickname is already in use.".format(
                            self.transport.getHost().host, attempted_nickname)
                        )

        self.users[self]["Hostmask"] = "{}!{}@{}".format(  # In the format of nickname!username@host
                            self.users[self]["Nickname"],
                            self.users[self]["Username"],
                            self.transport.getHost().host
                        )

        self.sendLine(":{} NICK {}".format("Praetor!*@127.0.0.1", "Penguin"))
        """
        pass

    def irc_NICK(self, prefix, params):
        attempted_nickname = params[0]

        # ToDo: Put this in a function. The hostmask is changed multiple times. DRY.
        if self.users[self]["Hostmask"] is None:
            self.users[self]["Hostmask"] = "{}!{}@{}".format(
                attempted_nickname,
                "*",
                self.users[self]["Host"]
            )

        current_nicknames = []
        for i in self.users:
            current_nicknames.append(self.users[i].get("Nickname"))

        # The nickname is taken.
        if attempted_nickname in current_nicknames:
            # The user instance has no nickname. This is the case on initial connection.
            if self.users[self]["Nicknames"] is None:
                # They've had 2 attempts at changing it - Generate one for them.
                if self.users[self]["Nickattempts"] >= 2:
                    # Create random nick
                    # Check if taken
                    # If it is, create another one.
                    # Repeat until not taken.
                    # Send new nick message, set the instance nick, set the hostmask
                    # Set Nickattempts to 0
                    pass
                else:
                    # Send nick in use
                    # Add one to nick attempts
                    # The client will (presumably) send another nick
                    # Then, it returns back to the top.
                    pass
            else:
                # The user already has a nick, so just send a line telling them its in use and keep things the same.
                pass
        else:
            if self.users[self]["Nickname"] is not None:
                # Send the new nick message
                # Set hostmask
                pass
            # Set the nickname in the self instance
            # Set hostmask
            pass



    def irc_USER(self, prefix, params):
        self.users[self]["Username"] = params[0]
        self.users[self]["Realname"] = params[3]
        self.users[self]["Channels"] = []
