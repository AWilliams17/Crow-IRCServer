from time import time
from util_modules.util_random_nick_generation import generate_random_nick


class IRCUser:
    illegal_characters = set(".<>'`()?*#+-")

    def __init__(self, protocol, username, nickname, realname, sign_on_time, last_msg_time, host, hostmask, channels,
                 nickattempts, nick_length, user_length, rplhelper, serverhost):
        self.protocol = protocol
        self.__username = username
        self.__nickname = nickname
        self.realname = realname
        self.sign_on_time = sign_on_time
        self.last_msg_time = last_msg_time
        self.host = host
        self.__hostmask = hostmask
        self.channels = channels
        self.nickattempts = nickattempts
        self.nick_length = nick_length
        self.user_length = user_length
        self.rplhelper = rplhelper
        self.rplhelper.user_instance = self
        self.server_host = serverhost
        self.modes = []
        self.status = "H"
        self.operator = False

    def __str__(self):
        return "Username: {}\nNickname: {}\nHostmask: {}\nChannels: {}\nNickattempts: {}\n".format(
            self.username, self.nickname, self.hostmask, self.channels, self.nickname
        )

    @property
    def hostmask(self):
        # Use * as an indicator that the username property of the hostmask wasn't set.
        # * is illegal as a username character so anyone using it would be booted, so it'll work.
        if self.__hostmask is not None and "*" in self.__hostmask:
            self.set_hostmask()
        return self.__hostmask

    def set_hostmask(self, nickname=None):
        username = "*"
        if self.username is not None:
            username = self.username
        if nickname is None:
            nickname = self.nickname
        self.__hostmask = "{}!{}@{}".format(nickname, username, self.host)

    @property
    def username(self):
        return self.__username

    @username.setter
    def username(self, username):
        username_length = len(username)

        if username_length == 0:
            raise ValueError("***Username can not be nothing.***")
        elif username_length > self.user_length:
            raise ValueError("***Username can not be greater than {} characters.***".format(self.user_length))
        elif any((c in self.illegal_characters) for c in username):
            raise ValueError("***Illegal Characters in Username.***")
        else:
            self.__username = username

    @property
    def nickname(self):
        return self.__nickname

    def set_nickname(self, desired_nickname, in_use_nicknames):
        """
        Handle first nickname set on client connection + subsequent nickname changes. If the desired nickname is the
        nickname the client is already using, then nothing will occur.
        """
        if self.hostmask is None:
            self.set_hostmask(desired_nickname)

        # Make sure it's not in use.
        if desired_nickname != self.nickname and desired_nickname in in_use_nicknames:
            # The user instance has no nickname. This is the case on initial connection.
            if self.nickname is None:
                if self.nickattempts != 2:
                    self.nickattempts += 1
                    return self.rplhelper.err_nicknameinuse(desired_nickname)
                # After giving them two tries to change it, generate one for them.
                randomized_nick = generate_random_nick(
                    self.protocol, in_use_nicknames, self.illegal_characters, self.nick_length
                )
                previous_hostmask = self.hostmask  # Store this since it's going to be changed
                self.__nickname = randomized_nick
                self.set_hostmask()
                self.nickattempts = 0
                return "Nickname attempts exceeded(2). A random nickname was generated for you." \
                       "\n:{} NICK {}".format(previous_hostmask, randomized_nick)
            # The user already has a nick, so just send a line telling them its in use and keep things the same.
            return self.notice("***Nickname is already in use.***")

        # If it's not in use, make sure it's a valid nickname.
        error = None
        if len(desired_nickname) > self.nick_length:
            error = ":Erroneous Nickname - Exceeded max char limit {}".format(self.nick_length)
        if any((c in self.illegal_characters) for c in desired_nickname):
            error = ":Erroneous Nickname - Illegal characters"
        if error is not None:
            if self.nickname is None:
                self.nickattempts += 1
                return self.rplhelper.err_erroneousnickname(desired_nickname, error)
            return self.notice(error, desired_nickname)

        # Check if they're renaming themselves, return rename_notice and also tell all the channels they're in.
        output = None
        if self.nickname is not None and self.nickname != desired_nickname or self.nickattempts != 0:
            if self.channels is not None:  # Send rename notice to any channels they're in
                for connected_channel in self.channels:
                    connected_channel.rename_user(self, desired_nickname)
            if self.nickattempts != 0 and self.nickname is None:  # This nickname is valid
                self.nickattempts = 0  # so set nickattempts to 0
            output = ":{} NICK {}".format(self.hostmask, desired_nickname)  # Tell them it was accepted.

        self.__nickname = desired_nickname
        self.set_hostmask()
        return output

    def send_msg(self, destination, message):
        """ Determine if a client is sending a message to a channel or user and handle appropriately. """
        if "*" in destination or "?" in destination:
            return self.rplhelper.err_badchanmask(destination)
        elif destination[0] == "#":
            if destination not in self.protocol.channels:
                return self.rplhelper.err_nosuchchannel()
            if self not in self.protocol.channels[destination].users:
                return self.rplhelper.err_cannotsendtochan(destination, "Cannot send to channel you are not in.")
            else:
                self.protocol.channels[destination].broadcast_message(message, self.hostmask)
                self.last_msg_time = time()
        else:
            for i in self.protocol.users:
                destination_user_protocol = self.protocol.users.get(i).protocol
                destination_nickname = self.protocol.users.get(i).nickname
                if destination_user_protocol == destination_user_protocol and destination_nickname == destination:
                    destination_user_protocol.privmsg(self.hostmask, destination, message)
                    self.last_msg_time = time()
            return self.rplhelper.err_nosuchnick()

    def away(self, reason):
        """ Mark a user as either away or unaway. If supplying no reason, assume they are marking as unaway. """
        if reason is None:
            self.status = "H"
            return self.rplhelper.rpl_unaway()
        else:
            self.status = "G"
            return self.rplhelper.rpl_nowaway()

    def set_mode(self, mode, accessor_nickname=None, accessor_is_operator=None):
        """ Handle a request to change a user's mode. Do not allow duplicate modes. Make sure it's valid. Make sure
         they have permission to do the change.
         """
        if accessor_nickname is None and accessor_is_operator is None:
            accessor_nickname = self.nickname
            accessor_is_operator = self.operator
        mode_char = mode[1]
        mode_addition = mode[0] == "+"
        mode_change_message = ":{} MODE {} :{}".format(accessor_nickname, self.nickname, mode)
        changing_own_modes = accessor_nickname == self.nickname

        if not changing_own_modes and not accessor_is_operator:
            return self.rplhelper.err_noprivileges("You can not affect someone else's modes.")

        if mode_char == "o":
            if not accessor_is_operator:
                return self.rplhelper.err_noprivileges()
            if not changing_own_modes:
                return self.rplhelper.err_noprivileges("You can not change someone else's operator flag.")
            if "o" not in self.modes:
                self.modes.append("o")
                return mode_change_message
            if not mode_addition:
                self.modes.remove("o")
                self.operator = False
                return mode_change_message + "\r\nYou are no longer an operator."
            return  # Do nothing- they're already an operator.

        if mode_char not in self.modes and mode_addition:
            self.modes.append(mode_char)
            return mode_change_message

        if mode_char in self.modes and not mode_addition:
            self.modes.remove(mode_char)
            return mode_change_message

    def get_modes(self, accessor_nickname=None, accessor_is_operator=None):
        """ Get a user's current modes for the requesting party (if they have permission) """
        if accessor_nickname is None and accessor_is_operator is None:
            accessor_nickname = self.nickname
            accessor_is_operator = self.operator
        checking_own_modes = accessor_nickname == self.nickname
        if not checking_own_modes and not accessor_is_operator:
            return self.rplhelper.err_noprivileges("You do not have permission to check someone else's modes.")
        return self.rplhelper.rpl_umodeis(self.nickname, self.modes)

    def notice(self, message, nick=None, send=False):
        """
        Send a notice to this user.
        """
        if nick is None:
            nick = self.nickname
        notice_message = ":{} NOTICE {} :{}".format(self.server_host, nick, message)
        if not send:
            return self.protocol.sendLine(notice_message)
        return notice_message
