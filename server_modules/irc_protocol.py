from twisted.words.protocols.irc import IRC, protocol, RPL_WELCOME
from twisted.internet.error import ConnectionLost
from server_modules.irc_channel import IRCChannel, QuitReason
from server_modules.irc_user import IRCUser
from server_modules.irc_rpl import RPLHelper
from time import time
from socket import getfqdn
from secrets import token_urlsafe


# noinspection PyPep8Naming
class IRCProtocol(IRC):
    """
    Represents a client's protocol. Dispatch incoming commands to the appropriate methods in irc_user and irc_channel
    and echo out command results to the client when needed. Additionally, maps the user and channels to the ChatServer
    in irc_server.
    In the irc_{COMMAND} methods, prefix remains unused as nothing ever gets passed to it from IRC. Not entirely sure
    what it is for.
    """
    def __init__(self, users, channels, config):
        """
        :param users: The current users on the server.
        :param channels: The current channels on the server.
        :param config: The dictionary generated from the server config file.
        This also contains a list of valid user modes...
        ToDo: Move that to the user class. Why is that here?
        """
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
        """
        On initial connection, get the time the connection was made for usage in lookups, get the max nick length
        and max username length from the config so the user objects know how big these can be. Then construct the
        user object.
        """
        current_time_posix = time()
        max_nick_length = self.config.NicknameSettings['MaxLength']
        max_user_length = self.config.UserSettings['MaxLength']
        self.sendLine("You are now connected to %s" % self.server_name)
        self.users[self] = IRCUser(
            self, None, None, None, current_time_posix, current_time_posix,
            self.transport.getPeer().host, None, [], 0, max_nick_length, max_user_length, self.rplhelper, self.hostname
        )

    def connectionLost(self, reason=protocol.connectionDone):
        """ When a client loses connection uncleanly. ToDo: Do the timeout messages properly. """
        if self in self.users:
            for channel in self.users[self].channels:
                quit_reason = QuitReason.UNSPECIFIED
                if reason.type == ConnectionLost:
                    quit_reason = QuitReason.TIMEOUT
                channel.remove_user(self.users[self], None, reason=quit_reason)
            del self.users[self]

    def irc_unknown(self, prefix, command, params):
        """ When an unknown command is sent to the server, this is the response sent back. """
        self.sendLine(self.rplhelper.err_unknowncommand(command))

    def irc_JOIN(self, prefix, params):
        """
        Called when a user sends a JOIN command to join a channel.
        At the moment, it only takes into account the first parameter.

        If the target channel does not exist, then it is created, and
        the user issuing the command is set as the owner and the details for
        the owner account of the channel is sent to him.

        :param params: List of arguments passed to the command. First member should be the channel name. Subsequent
        parameters are ignored for now until the functionality is added.
        :type params: list

        ToDo: Implement everything here:
        http://riivo.talviste.ee/irc/rfc/index.php?page=command.php&cid=8
        """
        if len(params) != 1:
            self.sendLine(self.rplhelper.err_needmoreparams("JOIN"))
            return

        channel = params[0].lower()
        if channel[0] != "#":
            channel = "#" + channel

        if self.users[self].nickname is None:
            self.sendLine("Failed to join channel: Your nickname is not set.")
            return

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
        """
        This is called when a user QUITs the network. Send a message to all the channels he is connected
        to with his client's LEAVE message (if supplied), and do cleanup.
        :param params: List of arguments passed to the command. The client should pass just one argument: The
        message he wishes to display to the channels when he leaves (his 'reason'). If not supplied, a generic
        message is used.
        :type params: list
        """
        leave_message = None
        if len(params) == 1:
            leave_message = params[0]
        if self in self.users:
            for channel in self.users[self].channels:
                channel.remove_user(self.users[self], leave_message, reason=QuitReason.DISCONNECTED)
            del self.users[self]

    def irc_PART(self, prefix, params):
        """
        This is called when a user LEAVES a channel (he "parts" from it). Send a message to the channel
        with the proper PART RPL and his leave message (if supplied).
        :param params: The list of arguments passed by the client. The first is the channel this was triggered on,
        and the second is the leave message sent by the client. If the client sends no leave message, then a generic
        message is used in it's place.
        :type params: list
        """
        channel = params[0]
        leave_message = None
        if len(params) == 2:
            leave_message = params[1]
        self.channels[channel].remove_user(self.users[self], leave_message, reason=QuitReason.LEFT)

    def irc_PRIVMSG(self, prefix, params):
        """
        Called when a client issues a PRIVMSG command, which is either sending a message to a server,
        or to another user.
        :param params: The list of arguments passed by the client to the command. The first argument should be the
        destination, and the second should be the channel or the user he wishes to send a message to.
        :type params: list
        """
        param_count = len(params)

        if param_count < 2:
            self.sendLine(self.rplhelper.err_needmoreparams("PRIVMSG"))
        else:
            results = self.users[self].send_msg(params[0], params[1])
            if results is not None:
                self.sendLine(results)

    def irc_NICK(self, prefix, params):
        """
        Called when a user attempts to change his nickname, or on the initial connection to set his nickname.
        :param params: The list of arguments passed to the command by the client. Should only be one: The nickname
        he wishes to use.
        :type params: list
        """
        attempted_nickname = params[0]
        in_use_nicknames = [x.users[x].nickname for x in self.users if x.users[x].nickname is not None]
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
        """
        TODO: This method needs some exception handling. What if param[0] and param[3] don't exist?
        Called when the client sends the USER message on initial connection to set the user's information.
        :param params: First argument is the username the client is using, the second one seems to be the same
        thing (?), the third is the clients host (unneeded - this is retrieved before here), and the fourth is
        the client's realname.
        :type params: list
        """
        username = params[0]
        realname = params[3]
        results = self.users[self].set_username(username, realname)
        if results is not None:  # Their username is invalid. Boot them.
            self.notice(self.hostname, results[0], results[1])
            self.transport.loseConnection()

    def irc_CAP(self, prefix, params):
        """
        Not implemented - this is supposed to return the list of capabilities supported by the server.
        https://ircv3.net/specs/core/capability-negotiation-3.1.html
        """
        pass

    def irc_WHO(self, prefix, params):
        """
        ToDo: Implement +i in the channel modes to prevent lookups
        ToDo: Also make sure i and I are the right modes.
        Called when a client issues a WHO command on a server, and when a client first connects to a channel
        (although I'm not sure about that last part. that seems to be what HexChat does atleast.)
        :param params: The list of arguments passed to the command. Argument one should be the channel to perform
        a lookup on.
        :type params: list
        """
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

    def irc_WHOIS(self, prefix, params):
        """
        ToDo: Implement +I to prevent lookups
        This is called when a client wants to perform a WHOIS lookup on another user.
        The client must be in the same channel as the channel the user he wishes to lookup is in.
        (I think that's how that works.)
        :param params: The list of arguments passed to the command by the client. Should just be one: The nickname the
        client wishes to perform the command on.
        :type params: list
        """
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
        self.sendLine(self.rplhelper.err_nosuchnick())

    def irc_AWAY(self, prefix, params):
        """
        This is called when a client issues an AWAY command to set himself as away.
        If a reason is not provided, the client is removing his away status.
        If a reason is provided, the client is setting his away status.
        :param params: List of arguments passed to the command. Should be one: the reason client is going away if
        setting himself as away, or if removing an away status, nothing.
        :type params: list
        """
        reason = None
        if len(params) != 0:
            reason = params[0]
        self.sendLine(self.users[self].away(reason))

    def irc_MODE(self, prefix, params):
        """
        This method is called when a client passes a mode command.
        The param count and param content for this method varies.
        :param params: The list of arguments passed to the command. Varies (explained below)
        :type params: list

        param count is 1 when looking up a locations modes, or looking up their own modes.
        param count is 2 when setting their own mode, setting a channel's mode, or checking another
        user's modes.
        param count is 3 when setting someone else's mode.
        """
        client_user = self.users[self]
        client_nickname_in_list = next((x for x in params if x == client_user.nickname), None)
        param_count = len(params)
        mode = next((x for x in params if x[0] in "+-" and len(x) >= 2), None)
        location_name = next((x for x in params if x[0] == "#"), None)

        # Make this an anonymous function since I don't want to do this loop unless I need to.
        def get_target_protocol():
            in_use_nicknames = [x.users[x].nickname for x in self.users if x.users[x].nickname is not None]
            target_nick = next((x for x in params if x != self.users[self].nickname and x in in_use_nicknames), None)
            _target_protocol = next((x for x in self.users if x.users[x].nickname == target_nick), None)
            return _target_protocol

        if param_count == 1:  # Checking a channel's modes, checking this client's modes.
            if client_nickname_in_list is None:
                if location_name is not None and location_name in self.channels:
                    self.sendLine(self.channels[location_name].get_modes())
                else:
                    self.sendLine(self.rplhelper.err_nosuchchannel())
            else:
                self.sendLine(client_user.get_modes(client_user))
        if param_count == 2:  # Setting this client's mode, setting a channel's mode, checking someone else's modes.
            if client_nickname_in_list is not None:
                if mode is None or mode[1] not in self.user_modes:
                    self.sendLine(self.rplhelper.err_unknownmode())
                else:
                    self.sendLine(client_user.set_mode(mode))
            else:
                target_protocol = get_target_protocol()
                if location_name is None:
                    if target_protocol is None:
                        self.sendLine(self.rplhelper.err_nosuchnick())
                    else:
                        self.sendLine(
                            self.users[target_protocol].get_modes()
                        )
                else:
                    if location_name not in self.channels:
                        self.sendLine(self.rplhelper.err_nosuchchannel())
                    else:
                        self.sendLine(
                            self.channels[location_name].set_mode(client_user.nickname, client_user.operator, mode)
                        )
        if param_count == 3:  # Setting another user's mode
            target_protocol = get_target_protocol()
            if target_protocol is None:
                self.sendLine(self.rplhelper.err_nosuchnick())
            #elif location_name is None:
            #    self.sendLine(self.rplhelper.err_notonchannel("You must share a channel with this user."))
            elif mode is None or mode[1] not in self.user_modes:
                self.sendLine(self.rplhelper.err_unknownmode())
            else:
                self.sendLine(target_protocol.set_mode(client_user.nickname, client_user.operator, mode))

    def irc_OPER(self, prefix, params):
        """
        This is called when a client issues an /oper command to login as an IRC administrator.
        :param params: List of arguments passed to the command. First argument should be the administrator username
        as defined in the config file, and the second should be the password associated with the account.
        :type params: list
        """
        user_nickname = self.users[self].nickname
        if len(params) != 2:
            self.sendLine(self.rplhelper.err_needmoreparams("OPER"))
            return
        username = params[0]
        password = params[1]
        if username in self.operators:
            if self.operators[username] == password:
                self.users[self].operator = True
                self.irc_MODE(self.user_modes, [user_nickname, "+o"])
                self.sendLine(self.rplhelper.rpl_youreoper())
                return
        self.sendLine(self.rplhelper.err_passwordmismatch())

    def irc_CHOPER(self, prefix, params):
        """ Not implemented - This is for logging in as a channel operator. """
        pass

    def irc_CHOWNER(self, prefix, params):
        """
        This is called when a user wishes to login as a channel operator for a channel.
        :param params: List containing arguments passed with the command. The first member should be the owner username,
        the second should be the owner password, and the third should be the channel to attempt to login to.
        :type params: list
        """
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
            self.sendLine(self.rplhelper.err_nosuchchannel())
            return

        results = self.channels[channel_name].login_owner(name, password, user)
        if results is not None:
            self.sendLine(results)
