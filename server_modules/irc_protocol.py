from twisted.words.protocols.irc import IRC, protocol, RPL_WELCOME
from twisted.internet.error import ConnectionLost
from server_modules.irc_channel import IRCChannel, QuitReason
from server_modules.irc_user import IRCUser
from util_modules.util_rplhelper import RPLHelper
from util_modules.util_param_count import param_count
from time import time
from socket import getfqdn
from secrets import token_urlsafe
# TODO: NOTE - Nickname changing after erroneous nick is sent is broken!
# noinspection PyPep8Naming


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
        print("------------------------------")

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
        # ToDo: Implement everything here: http://riivo.talviste.ee/irc/rfc/index.php?page=command.php&cid=8

        if self.users[self].nickname is None:
            return self.sendLine("Failed to join channel: Your nickname is not set.")

        channel = params[0].lower()
        if channel[0] != "#":
            channel = "#" + channel

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
        self.channels[channel].add_user(self.users[self])

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
        params_count = len(params)

        if params_count < 2:
            self.sendLine(self.rplhelper.err_needmoreparams("PRIVMSG"))
        else:
            results = self.users[self].send_msg(params[0], params[1])
            if results is not None:
                self.sendLine(results)

    def irc_NICK(self, prefix, params):
        attempted_nickname = params[0]
        in_use_nicknames = [self.users[x].nickname for x in self.users if self.users[x].nickname is not None]
        if self.users[self].nickname is None and self.users[self].nickattempts == 0:
            self.sendLine(":{} {} {} :{}".format(
                self.hostname, RPL_WELCOME,
                attempted_nickname,
                self.config.ServerSettings["ServerWelcome"] + " {}".format(attempted_nickname))
            )
        results = self.users[self].set_nickname(attempted_nickname, in_use_nicknames)
        if results is not None:
            self.sendLine(results)

    def irc_USER(self, prefix, params):
        username = params[0]
        realname = params[3]
        try:
            self.users[self].realname = realname
            self.users[self].username = username
        except ValueError as e:
            self.sendLine(str(e))
            self.transport.loseConnection()

    def irc_CAP(self, prefix, params):
        """
        Not implemented - this is supposed to return the list of capabilities supported by the server.
        https://ircv3.net/specs/core/capability-negotiation-3.1.html
        """
        pass

    def irc_WHO(self, prefix, params):
        target_channel = params[0]
        if target_channel in self.channels:
            results = self.channels[target_channel].who(self.users[self], self.hostname)
            if type(results) is not str:  # Valid return type should be a list. Invalid is a string.
                return self.who(self.users[self].nickname, target_channel, results)
            return self.sendLine(results)
        return self.sendLine(self.rplhelper.err_nosuchchannel())

    def irc_WHOIS(self, prefix, params):
        target_nickname = params[0]
        target_user = next((self.users[x] for x in self.users if self.users[x].nickname == target_nickname), None)
        if target_user is not None:
            target_username = target_user.username
            target_hostmask = target_user.hostmask
            target_realname = target_user.realname
            target_server_name = self.server_name
            target_server_description = self.server_description
            target_is_operator = target_user.operator
            target_last_msg_time = time() - target_user.last_msg_time
            target_signon_time = target_user.sign_on_time
            target_channels = [x.channel_name for x in target_user.channels]
            receiver_nickname = self.users[self].nickname
            if len(target_channels) == 0:
                target_channels.append("User is not in any channels.")
            return self.whois(
                receiver_nickname, target_nickname, target_username, target_hostmask, target_realname,
                target_server_name, target_server_description, target_is_operator, target_last_msg_time,
                target_signon_time, target_channels
            )
        return self.sendLine(self.rplhelper.err_nosuchnick())

    def irc_AWAY(self, prefix, params):
        reason = None
        if len(params) != 0:
            reason = params[0]
        self.sendLine(self.users[self].away(reason))

    def irc_MODE(self, prefix, params):
        param_count = len(params)
        this_client = self.users[self]  # Check if this client's nickname is in the params.
        client_nickname_in_list = next((x for x in params if x == this_client.nickname), None)
        mode = next((x for x in params if x[0] in "+-" and len(x) >= 2), None)
        location_name = next((x for x in params if x[0] == "#"), None)

        # Make this an anonymous function since I don't want to do this loop unless I need to.
        def get_target_protocol():
            in_use_nicknames = [x.users[x].nickname for x in self.users if x.users[x].nickname is not None]
            target_nick = next((x for x in params if x != self.users[self].nickname and x in in_use_nicknames), None)
            _target_protocol = next((x for x in self.users if x.users[x].nickname == target_nick), None)
            return _target_protocol

        if param_count == 1:  # Checking a channel's modes, checking this client's modes.
            if client_nickname_in_list is None and location_name is not None and location_name in self.channels:
                return self.sendLine(self.channels[location_name].get_modes())
            elif client_nickname_in_list is None and location_name is None:
                return self.sendLine(self.rplhelper.err_nosuchchannel())
            return self.sendLine(this_client.get_modes())

        if param_count == 2:  # Setting this client's mode, setting a channel's mode, checking someone else's modes.
            if client_nickname_in_list is None:
                target_protocol = get_target_protocol()
                if location_name is None:
                    if target_protocol is None:
                        return self.sendLine(self.rplhelper.err_nosuchnick())
                    return self.sendLine(self.users[target_protocol].get_modes(this_client.nickname, this_client.operator))
                else:
                    if location_name in self.channels:
                        return self.sendLine(self.channels[location_name].set_mode(mode))
                    return self.sendLine(self.rplhelper.err_nosuchchannel())
            if mode is not None and mode[1] in self.user_modes:
                return self.sendLine(this_client.set_mode(mode))
            return self.sendLine(self.rplhelper.err_unknownmode())

        if param_count == 3:  # Setting another user's mode
            target_protocol = get_target_protocol()
            if target_protocol is None:
                return self.sendLine(self.rplhelper.err_nosuchnick())
            elif mode is None or mode[1] not in self.user_modes:
                return self.sendLine(self.rplhelper.err_unknownmode())
            else:
                return self.sendLine(self.users[target_protocol].set_mode(mode, this_client.nickname, this_client.operator))

    def irc_OPER(self, prefix, params):
        user = self.users[self]
        if user.operator:
            return self.sendLine("You are already an operator.")
        if len(params) != 2:
            return self.sendLine(
                self.rplhelper.err_needmoreparams("OPER") +
                "\r\nUsage: OPER <username> <password> - Logs you in as an IRC operator."
            )
        username = params[0]
        password = params[1]
        if username in self.operators:
            if self.operators[username] == password:
                user.operator = True
                return self.sendLine(user.set_mode("+o") + "\r\n" + self.rplhelper.rpl_youreoper())
        self.sendLine(self.rplhelper.err_passwordmismatch())

    def irc_CHOPER(self, prefix, params):
        """ Not implemented - This is for logging in as a channel operator. """
        pass

    def irc_CHOWNER(self, prefix, params):
        if len(params) < 3:
            self.sendLine(self.rplhelper.err_needmoreparams("CHOWNER"))
            return self.sendLine(
                self.rplhelper.err_needmoreparams("CHOWNER") +
                "\r\nUsage: CHOWNER <owner_name> <owner_pass> <channel> - Logs in to the specified channel as an owner."
            )
        if params[2][0] != "#":
            params[2] = "#" + params[2]
        name = params[0]
        password = params[1]
        channel_name = params[2]
        user = self.users[self]
        if channel_name not in self.channels:
            return self.sendLine(self.rplhelper.err_nosuchchannel())

        self.sendLine(self.channels[channel_name].login_owner(name, password, user))
