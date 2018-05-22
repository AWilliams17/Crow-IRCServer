from time import time
from random import sample, choice
from string import ascii_lowercase, ascii_uppercase, digits


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
        return self.__hostmask

    def set_hostmask(self, nickname):
        username = "*"
        if self.username is not None:
            username = self.username
        self.__hostmask = "{}!{}@{}".format(
            nickname,
            username,
            self.host
        )

    @property
    def username(self):
        return self.__username

    def set_username(self, username, realname):
        username_length = len(username)

        if username_length == 0:
            return [self.nickname, "***Username can not be nothing.***"]
        if username_length > self.user_length:
            return [self.nickname, "***Username can not be greater than {} characters.***".format(self.user_length)]
        if any((c in self.illegal_characters) for c in username):
            return [self.nickname, "***Illegal Characters in Username.***"]

        self.__username = username
        self.realname = realname
        return None

    @property
    def nickname(self):
        return self.__nickname

    def set_nickname(self, desired_nickname, in_use_nicknames):
        """ Handle first nickname set on client connection + subsequent nickname changes. """
        if self.hostmask is None:
            self.set_hostmask(desired_nickname)

        if desired_nickname == self.nickname:
            return None

        if desired_nickname in in_use_nicknames:
            # The user instance has no nickname. This is the case on initial connection.
            if self.nickname is None:
                # They've had 2 attempts at changing it - Generate one for them.
                if self.nickattempts != 2:
                    self.nickattempts += 1
                    return self.rplhelper.err_nicknameinuse(desired_nickname)
                else:
                    randomized_nick = self._generate_random_nick(in_use_nicknames)
                    previous_hostmask = self.hostmask  # Store this since it's going to be changed
                    self.__nickname = randomized_nick
                    self.set_hostmask(self.nickname)
                    output = "Nickname attempts exceeded(2). A random nickname was generated for you."
                    output += "\n:{} NICK {}".format(previous_hostmask, randomized_nick)
                    return output
            else:
                # The user already has a nick, so just send a line telling them its in use and keep things the same.
                return ":{} NOTICE {} :***Nickname is already in use.***".format(self.server_host, self.nickname)

        # ToDo: Try to combine these
        if len(desired_nickname) > self.nick_length:
            error = "Exceeded max char limit {}".format(self.nick_length)
            if self.__nickname is None:
                self.nickattempts += 1
                return self.rplhelper.err_erroneousnickname(desired_nickname, error)
            return ":{} 436 * {} :{} ".format(self.server_host, desired_nickname, error)  # ToDo: Make this a notice

        if any((c in self.illegal_characters) for c in desired_nickname):
            error = ":Erroneous Nickname - Illegal characters".format(self.nick_length)
            if self.nickname is None:
                self.nickattempts += 1
                return self.rplhelper.err_erroneousnickname(desired_nickname, error)
            return ":{} 436 * {} :{}".format(self.server_host, desired_nickname, error)  # ToDo: Make this a notice

        output = None
        if self.nickname is not None or self.nickattempts != 0:  # They are renaming themselves.
            if self.channels is not None:  # Send rename notice to any channels they're in
                for connected_channel in self.channels:
                    connected_channel.rename_user(self, desired_nickname)
            if self.nickattempts != 0 and self.nickname is None:  # This nickname is valid
                self.nickattempts = 0  # so set nickattempts to 0
            output = ":{} NICK {}".format(self.hostmask, desired_nickname)  # Tell them it was accepted.

        self.__nickname = desired_nickname
        self.set_hostmask(desired_nickname)
        return output  # Return any errors/any rename notices.

    def send_msg(self, destination, message):
        """ Determine if a client is sending a message to a channel or user and handle appropriately. """
        if "*" in destination or "?" in destination:
            return self.rplhelper.err_badchanmask(destination)
        if destination[0] == "#":
            if destination not in self.protocol.channels:
                return self.rplhelper.err_nosuchchannel(destination)
            if self not in self.protocol.channels[destination].users:
                return self.rplhelper.err_cannotsendtochan(destination, "Cannot send to channel you are not in.")
            else:
                self.protocol.channels[destination].broadcast_message(message, self.hostmask)
                self.last_msg_time = time()
                return None
        if destination[0] != "#":
            for i in self.protocol.users:
                destination_user_protocol = self.protocol.users.get(i).protocol
                destination_nickname = self.protocol.users.get(i).nickname
                if destination_user_protocol == destination_user_protocol and destination_nickname == destination:
                    destination_user_protocol.privmsg(self.hostmask, destination, message)
                    self.last_msg_time = time()
                    return None
            return self.rplhelper.err_nosuchnick(destination)

    def away(self, reason):
        if reason is None:
            self.status = "H"
            return self.rplhelper.rpl_unaway()
        else:
            self.status = "G"
            return self.rplhelper.rpl_nowaway()

    def set_op(self):
        self.operator = True

    # ToDo: This can be majorly improved.
    def set_mode(self):
        """ Handle a request to change a user's mode. Do not allow duplicate modes. Make sure it's valid. Make sure
         they have permission to do the change."""


        pass

    def get_modes(self, nick, location=None):
        """ Get a user's current modes (if they have permission) """
        modes = self.modes
        if nick != self.nickname and self.operator:
            if location not in self.channels or nick not in location.get_nicknames():
                return self.rplhelper.err_notonchannel("You must share a channel with this user.")
            target_user_instance = [x for x in location.users if x.nickname == nick][0]
            modes = target_user_instance.modes
        elif nick != self.nickname and not self.operator:
            return self.rplhelper.err_noprivileges()
        return self.rplhelper.rpl_umodeis(nick, modes)

    def notice(self, message):
        self.protocol.sendLine(":{} NOTICE {} :{}".format(self.server_host, self.nickname, message))

    def _generate_random_nick(self, current_nicknames):
        """ When a client exceeds the max nick attempt limit, generate one for them. """
        protocol_instance_string = str(self.protocol).replace(" ", "")
        random_nick = ''.join(sample(protocol_instance_string, len(protocol_instance_string)))
        random_nick_s = ''.join([c for c in random_nick[:self.nick_length] if c not in self.illegal_characters])

        def validate_nick(nick, current_nicks):  # Check if the nick is still conflicting. Generate new one if yes.
            if nick in current_nicknames:
                def generate_junk(amount):
                    return ''.join([
                        choice(
                            ascii_lowercase +
                            ascii_uppercase +
                            digits) for i in range(amount)
                    ])

                # Re shuffle the string + Add random garbage to it and then re-validate it, keep it under nick length
                nick = (''.join(sample(nick, len(nick))) + generate_junk(15))[:self.nick_length]
                validate_nick(nick, current_nicks)
            return nick

        random_nick_s = validate_nick(random_nick_s, current_nicknames)
        return random_nick_s
