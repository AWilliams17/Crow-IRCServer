from twisted.words.protocols.irc import IRC, protocol, RPL_WELCOME
from twisted.internet.error import ConnectionLost
from server_modules.irc_channel import IRCChannel, QuitReason
from server_modules.irc_user import IRCUser
from server_modules.irc_rpl import RPLHelper
from time import time
from socket import getfqdn
from secrets import token_urlsafe
# ToDo: !-->Refactor<--!
# ToDo: Implement channel owner functions + channel operators
# ToDo: Clean up irc_MODE, clean up set_mode, test the channel owner login more thoroughly
# ToDo: Figure out what HOP count does
# ToDo: Make +I Work
# ToDo: Add more modes + channel modes
# ToDo: Implement CAP
# ToDo: Implement max clients
# ToDo: Implement PING/PONG (since I guess it doesn't work?)


class IRCProtocol(IRC):
    def __init__(self, users, channels, config):
        self.users = users
        self.channels = channels
        self.config = config
        self.server_name = self.config.ServerSettings['ServerName']
        self.server_description = self.config.ServerSettings['ServerDescription']
        self.operators = self.config.UserSettings["Operators"]
        self.hostname = getfqdn()
        self.rplhelper = RPLHelper(None)
        self.user_modes = ['I', 'o']  # ToDo: More

    def connectionMade(self):
        current_time_posix = time()
        max_nick_length = self.config.NicknameSettings['MaxLength']
        max_user_length = self.config.UserSettings['MaxLength']
        self.sendLine("You are now connected to %s" % self.server_name)
        self.users[self] = IRCUser(
            self, None, None, None, current_time_posix, current_time_posix,
            self.transport.getPeer().host, None, [], 0, max_nick_length, max_user_length, self.rplhelper, self.hostname
        )

    def connectionLost(self, reason=protocol.connectionDone):
        if self in self.users:
            for channel in self.users[self].channels:
                quit_reason = QuitReason.UNSPECIFIED
                if reason.type == ConnectionLost:
                    quit_reason = QuitReason.TIMEOUT
                channel.remove_user(self.users[self], None, reason=quit_reason)
            del self.users[self]

    def irc_unknown(self, prefix, command, params):
        self.sendLine(self.rplhelper.err_unknowncommand(command))

    def irc_JOIN(self, prefix, params):
        if len(params) != 1:
            self.sendLine(self.rplhelper.err_needmoreparams("JOIN"))
            return

        channel = params[0].lower()
        if channel[0] != "#":
            channel = "#" + channel

        if self.users[self].nickname is None:
            self.sendLine("Failed to join channel: Your nickname is not set.")
            return

        # The channel doesn't exist on the network - create it and make an owner account for the creator.
        # Note: The account really isn't secure, but it'll do.
        if channel not in self.channels:
            owner_name = token_urlsafe(16)
            owner_password = token_urlsafe(32)
            self.channels[channel] = IRCChannel(channel)
            self.channels[channel].channel_owner = self.users[self]
            self.channels[channel].channel_owner_account = [owner_name, owner_password]
            self.users[self].send_msg(
                self.users[self].nickname,
                "You are now logged in as the owner of {}".format(channel)
            )
            self.users[self].send_msg(
                self.users[self].nickname,
                "Owner account details are: {}:{} - Don't lose them.".format(owner_name, owner_password)
            )

        # Map this protocol instance to the channel's current clients,
        # and then add this channel to the list of channels the user is connected to.
        results = self.channels[channel].add_user(self.users[self])
        if results is not None:
            self.sendLine(self.rplhelper.err_nonicknamegiven(results))

    def irc_QUIT(self, prefix, params):
        leave_message = None
        if len(params) == 1:
            leave_message = params[0]
        if self in self.users:
            for channel in self.users[self].channels:
                channel.remove_user(self.users[self], leave_message, reason=QuitReason.DISCONNECTED)
            del self.users[self]

    def irc_PART(self, prefix, params):
        channel = params[0]
        leave_message = None
        if len(params) == 2:
            leave_message = params[1]
        self.channels[channel].remove_user(self.users[self], leave_message, reason=QuitReason.LEFT)

    def irc_PRIVMSG(self, prefix, params):
        param_count = len(params)

        if param_count < 2:
            self.sendLine(self.rplhelper.err_needmoreparams("PRIVMSG"))
        else:
            results = self.users[self].send_msg(params[0], params[1])
            if results is not None:
                self.sendLine(results)

    def irc_NICK(self, prefix, params):
        attempted_nickname = params[0]
        if self.users[self].nickname is None and self.users[self].nickattempts == 0:
            self.sendLine(":{} {} {} :{}".format(
                self.hostname, RPL_WELCOME,
                attempted_nickname,
                self.config.ServerSettings["ServerWelcome"] + " {}".format(attempted_nickname))
            )

        results = self.users[self].set_nickname(attempted_nickname)
        if results is not None:
            self.sendLine(results)

    def irc_USER(self, prefix, params):
        username = params[0]
        realname = params[3]
        results = self.users[self].set_username(username, realname)
        if results is not None:  # Their username is invalid. Boot them.
            self.notice(self.hostname, results[0], results[1])
            self.transport.loseConnection()

    def irc_CAP(self, prefix, params):
        pass

    # ToDo: Refactor.
    def irc_WHO(self, prefix, params):
        if params[0] in self.channels:
            results = self.channels[params[0]].who(
                self.users[self],
                self.transport.getHost().host)
            if results is not None:
                self.who(self.users[self].nickname, params[0], results)
                return
        self.sendLine(":{} 315 {} {} :End of /WHO list.".format(
            self.hostname,
            self.users[self].nickname,
            params[0])
        )

    # ToDo: Refactor.
    def irc_WHOIS(self, prefix, params):
        for user in self.users:
            if self.users[user].nickname == params[0]:
                user_channels = [x.channel_name for x in self.users[user].channels]
                if len(user_channels) == 0:
                    user_channels.append("User is not in any channels.")
                self.whois(
                    self.users[self].nickname, params[0], self.users[user].username,
                    self.users[user].hostmask, self.users[user].realname, self.server_name,
                    self.server_description, self.users[self].operator, time() - self.users[user].last_msg_time,
                    self.users[user].sign_on_time, user_channels
                )
                return
        self.sendLine(self.rplhelper.err_nosuchnick(params[0]))

    def irc_AWAY(self, prefix, params):
        reason = None
        if len(params) != 0:
            reason = params[0]
        self.sendLine(self.users[self].away(reason))

    # ToDo: This is a massive mess. Fix this.
    def irc_MODE(self, prefix, params):
        location = None
        nick = None
        mode = None

        if len(params) == 3:
            if params[0][0] == "#":
                location = self.channels[params[0]]
            nick = params[1]
            mode = params[2]
        elif len(params) == 2:
            if len(params[1]) > 2:
                location = params[0]
                nick = params[1]
                if location[0] != "#":
                    self.sendLine(self.rplhelper.err_notonchannel("You must share a channel with this user."))
                    return
                if location not in [x for x in self.channels]:
                    self.sendLine(self.rplhelper.err_nosuchchannel(location))
                    return
                location = self.channels[location]
                self.sendLine(self.users[self].get_modes(nick, location))
                return
            else:
                nick = params[0]
                mode = params[1]
        elif len(params) == 1:
            if params[0][0] != "#":
                nick = params[0]
                self.sendLine(self.users[self].get_modes(nick))
            else:  # ToDo: Channel modes
                location = self.channels[params[0]]
                #self.sendLine(self.channels[params[0]].get_modes(location))
            return

        result = self.users[self].set_mode(location, nick, mode, self.user_modes)
        if result is not None:
            self.sendLine(result)

    def irc_OPER(self, prefix, params):  # ToDo: ERR_NOOPERHOST
        user_nickname = self.users[self].nickname
        if len(params) != 2:
            self.sendLine(self.rplhelper.err_needmoreparams("OPER"))
            return
        username = params[0]
        password = params[1]
        if username in self.operators:
            if self.operators[username] == password:
                self.users[self].set_op()
                self.irc_MODE(self.user_modes, [user_nickname, "+o"])
                self.sendLine(self.rplhelper.rpl_youreoper())
                return
        self.sendLine(self.rplhelper.err_passwordmismatch())

    def irc_CHOPER(self, prefix, params):
        pass

    def irc_CHOWNER(self, prefix, params):
        if len(params) < 3:
            self.sendLine(self.rplhelper.err_needmoreparams(
                "3 parameters needed: <owner account name> <owner pass> #<channel>"
            ))
            return
        if params[2][0] != "#":
            params[2] = "#" + params[2]
        name = params[0]
        password = params[1]
        channel_name = params[2]
        user = self.users[self]
        if channel_name not in self.channels:
            self.sendLine(self.rplhelper.err_nosuchchannel(channel_name))
            return

        results = self.channels[channel_name].login_owner(name, password, user)
        if results is not None:
            self.sendLine(results)
