from twisted.words.protocols.irc import IRC, protocol, RPL_WELCOME
from server.irc_channel import IRCChannel, QuitReason
from server.irc_user import IRCUser
from server.irc_ratelimiter import rate_limiter
from server.irc_rplhelper import RPLHelper
from server.irc_param_count import min_param_count
from server.irc_config import IRCConfig
from time import time
from socket import getfqdn
from secrets import token_urlsafe

# noinspection PyPep8Naming


class IRCProtocol(IRC):
    def __init__(self, users, channels, config, ratelimiter, clientlimiter, pingmanager, channelmanager):
        """
        Create a protocol instance for this client + set up a user/rplhelper instance. Pass references
        to the ratelimiter, clientlimiter, pingmanager, and channelmanager.
        Args:
            users (OrderedDict): The server's current logged users.
            channels (OrderedDict): The server's current channels.
            config (IRCConfig): The server's config settings.
        """
        self.users = users
        self.channels = channels
        self.config = config
        self.server_name = self.config.ServerSettings.ServerName
        self.server_description = self.config.ServerSettings.ServerDescription
        self.operators = self.config.UserSettings.Operators
        self.hostname = getfqdn()
        self.client_host = None
        self.rplhelper = RPLHelper(None)
        self.user_instance = None
        self.ratelimiter = ratelimiter
        self.clientlimiter = clientlimiter
        self.pingmanager = pingmanager
        self.channelmanager = channelmanager

    def connectionMade(self):
        current_time_posix = time()
        max_nick_length = self.config.UserSettings.MaxNicknameLength
        max_user_length = self.config.UserSettings.MaxUsernameLength
        max_clients = self.config.UserSettings.MaxClients
        self.client_host = self.transport.getPeer().host
        self.clientlimiter.add_entry(self.client_host)
        if self.clientlimiter.host_has_too_many_clients(self.client_host, max_clients):
            self.sendLine("You have too many clients connected to the server. Max clients: {}".format(max_clients))
            self.transport.loseConnection()
        else:
            self.sendLine("You are now connected to %s" % self.server_name)
            self.user_instance = IRCUser(
                self, None, None, None, current_time_posix, current_time_posix,
                self.client_host, None, [], 0, max_nick_length, max_user_length, self.rplhelper, self.hostname
            )
            self.users[self] = self.user_instance

    def connectionLost(self, reason=protocol.connectionDone):
        # Make sure all circular references created by this object get cleaned up.
        self.clientlimiter.remove_entry(self.client_host)
        self.pingmanager.remove_from_queue(self)
        if self in self.users:
            for channel in self.user_instance.channels:
                quit_reason = QuitReason.UNSPECIFIED
                channel.remove_user(self.user_instance, None, reason=quit_reason)
            del self.users[self]
        self.user_instance = None
        self.rplhelper.user_instance = None

    def irc_unknown(self, prefix, command, params):
        self.sendLine(self.rplhelper.err_unknowncommand(command))

    def irc_PONG(self, prefix, params):
        self.pingmanager.pong_received(self, params)

    @min_param_count(1)
    def irc_JOIN(self, prefix, params):
        """ When a user attempts to join a channel, prevent them if they have no nickname. Otherwise, check if the
         channel name exists. If it doesn't, make a new channel and put them as the owner, send them the owner
         details. Otherwise, try to have the channel add them."""
        # ToDo: Implement everything here: http://riivo.talviste.ee/irc/rfc/index.php?page=command.php&cid=8

        if self.user_instance.nickname is None:
            return self.sendLine("Failed to join channel: Your nickname is not set.")

        channel = params[0].lower()
        if channel[0] != "#":
            channel = "#" + channel

        if channel not in self.channels:
            owner_name = token_urlsafe(16)
            owner_password = token_urlsafe(32)
            new_channel = IRCChannel(channel, self.channelmanager)
            new_channel.channel_owner = self.user_instance
            new_channel.channel_owner_account = [owner_name, owner_password]
            new_channel.last_owner_login = int(time())
            self.channels[channel] = new_channel
            self.user_instance.send_msg(
                self.user_instance.nickname,
                "You are now logged in as the owner of {}".format(channel)
            )
            self.user_instance.send_msg(
                self.user_instance.nickname,
                "Owner account details for {} are: {}:{} - Don't lose them.".format(channel, owner_name, owner_password)
            )

        # Map this protocol instance to the channel's current clients,
        # and then add this channel to the list of channels the user is connected to.
        # If any errors occur, echo them to the client.
        results = self.channels[channel].add_user(self.user_instance)
        if results is not None:
            self.sendLine(results)

    def irc_QUIT(self, prefix, params, timeout_seconds=None):
        """ When a user disconnects from the server, check if their client issued a leave message. If not, a default
         one will be used. Remove the user from the channels the client was in w/ the leave message."""
        leave_message = None
        quit_reason = QuitReason.DISCONNECTED
        if timeout_seconds is not None:
            quit_reason = QuitReason.TIMEOUT
            self.transport.loseConnection()
        if len(params) == 1:
            leave_message = params[0]
        if self in self.users:
            for channel in self.user_instance.channels:
                channel.remove_user(self.user_instance, leave_message, reason=quit_reason,
                                    timeout_seconds=timeout_seconds)
            del self.users[self]

    @min_param_count(1)
    def irc_PART(self, prefix, params):
        """ When a user leaves a channel, check if their client issued a leave message. If not, a default
         one will be used. Remove the user from the channel the client was in w/ the leave message."""
        channel = params[0]
        leave_message = None
        if len(params) == 2:
            leave_message = params[1]
        self.channels[channel].remove_user(self.user_instance, leave_message, reason=QuitReason.LEFT)

    @min_param_count(2)
    def irc_PRIVMSG(self, prefix, params):
        results = self.user_instance.send_msg(params[0], params[1])
        if results is not None:
            self.sendLine(results)

    @min_param_count(1)
    def irc_NICK(self, prefix, params):
        """ When a client issues a NICK command on join/to rename themselves, generate a list of in use nicknames,
         also if this is their first time connecting, send them a welcome with the nickname. (to be moved later)"""
        attempted_nickname = params[0]
        in_use_nicknames = [self.users[x].nickname for x in self.users if self.users[x].nickname is not None]
        if self.user_instance.nickname is None and self.user_instance.nickattempts == 0:
            self.sendLine(":{} {} {} :{}".format(
                self.hostname, RPL_WELCOME,
                attempted_nickname,
                self.config.ServerSettings.ServerWelcome + ", {}!".format(attempted_nickname))
            )
        results = self.user_instance.set_nickname(attempted_nickname, in_use_nicknames)
        if results is not None:
            self.sendLine(results)

    def irc_USER(self, prefix, params):
        """ When a user first joins the client sends a USER command with information about the client. Verify it's
        all valid. If it's not valid, then kick them."""
        try:
            username = params[0]
            realname = params[3]
            self.user_instance.username = username
            self.user_instance.realname = realname
        except (ValueError, IndexError) as e:
            error_message = str(e)
            if type(e) == IndexError:
                error_message = "*** Your client did not supply enough parameters to make a valid USER command. ***"
            self.sendLine(error_message)
            self.transport.loseConnection()

    def irc_CAP(self, prefix, params):
        """
        Not implemented - this is supposed to return the list of capabilities supported by the server.
        https://ircv3.net/specs/core/capability-negotiation-3.1.html
        """
        pass

    @min_param_count(1)
    def irc_WHO(self, prefix, params):
        """ Attempt to perform a WHO lookup on a channel """
        target_channel = params[0]
        if target_channel in self.channels:
            results = self.channels[target_channel].who(self.user_instance, self.hostname)
            if type(results) is not str:  # Valid return type should be a list. Invalid is a string.
                return self.who(self.user_instance.nickname, target_channel, results)
            return self.sendLine(results)
        return self.sendLine(self.rplhelper.err_nosuchchannel())

    @min_param_count(1)
    def irc_WHOIS(self, prefix, params):
        """ Attempt to perform a WHOIS on another user."""
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
            receiver_nickname = self.user_instance.nickname
            if len(target_channels) == 0:
                target_channels.append("User is not in any channels.")
            return self.whois(
                receiver_nickname, target_nickname, target_username, target_hostmask, target_realname,
                target_server_name, target_server_description, target_is_operator, target_last_msg_time,
                target_signon_time, target_channels
            )
        return self.sendLine(self.rplhelper.err_nosuchnick())

    def irc_AWAY(self, prefix, params):
        """ If a reason is supplied by the user, then it is assumed they are setting themselves away. Otherwise it is
         assumed they are marking themselves as unaway. """
        reason = None
        if len(params) != 0:
            reason = params[0]
        self.sendLine(self.user_instance.away(reason))

    @min_param_count(1)
    def irc_MODE(self, prefix, params):
        """ Called when a user either:
            A: Wants to check their own modes (params will be 1), [their_nickname]
            B: Wants to check someone else's modes (params will be 2), [location_it_occurred_in, target_nick]
            C: Wants to check a channel's modes (params will be 1), [the_channel]
            D: Wants to set their own mode (params will be 2), [their_nickname, mode]
            E: Wants to set someone else's mode (params will be 3), [location, target_nick, mode]
            F: Wants to set a channel's mode. (params will be 2), [location, mode]
            ToDo: Slated for (another) rewrite
         """
        param_count = len(params)
        this_client = self.user_instance  # Check if this client's nickname is in the params.
        client_nickname_in_list = next((x for x in params if x == this_client.nickname), None)
        mode = next((x for x in params if x[0] in "+-" and len(x) >= 2), None)
        location_name = next((x for x in params if x[0] == "#"), None)

        # Make this an anonymous function since I don't want to do this loop unless I need to.
        def get_target_protocol():
            in_use_nicknames = [x.users[x].nickname for x in self.users if x.users[x].nickname is not None]
            target_nick = next((x for x in params if x != self.user_instance.nickname and x in in_use_nicknames), None)
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
            if mode is not None:
                return self.sendLine(this_client.set_mode(mode))
            return self.sendLine(self.rplhelper.err_unknownmode())

        if param_count == 3:  # Setting another user's mode
            target_protocol = get_target_protocol()
            if target_protocol is None:
                return self.sendLine(self.rplhelper.err_nosuchnick())
            elif mode is None:
                return self.sendLine(self.rplhelper.err_unknownmode())
            else:
                return self.sendLine(self.users[target_protocol].set_mode(mode, this_client.nickname, this_client.operator))

    @rate_limiter("OPER", 10)
    @min_param_count(2, "Usage: OPER <username> <password> - Logs you in as an IRC operator.")
    def irc_OPER(self, prefix, params):
        user = self.user_instance
        if user.operator:
            return self.sendLine("You are already an operator.")
        username = params[0]
        password = params[1]
        if username in self.operators:
            if self.operators[username] == password:
                user.operator = True
                return self.sendLine(user.set_mode("+o") + "\r\n" + self.rplhelper.rpl_youreoper())
        self.sendLine(self.rplhelper.err_passwordmismatch())

    @rate_limiter("CHOPER", 5)
    def irc_CHOPER(self, prefix, params):
        """ Not implemented - This is for logging in as a channel operator. """
        pass

    def irc_COMMANDS(self, prefix, params):
        """ Not implemented - return a list of commands the server uses """
        pass

    @rate_limiter("CHOWNER", 10)
    @min_param_count(3, "Usage: CHOWNER <owner_name> <pass> <channel> - Logs in to the specified channel as an owner.")
    def irc_CHOWNER(self, prefix, params):
        if len(params) < 3:
            self.sendLine(self.rplhelper.err_needmoreparams("CHOWNER"))
        if params[2][0] != "#":
            params[2] = "#" + params[2]
        name = params[0]
        password = params[1]
        channel_name = params[2]
        user = self.user_instance
        if channel_name not in self.channels:
            return self.sendLine(self.rplhelper.err_nosuchchannel())
        self.sendLine(self.channels[channel_name].login_owner(name, password, user))
