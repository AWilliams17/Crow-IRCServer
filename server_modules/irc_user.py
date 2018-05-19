from random import sample, choice
from string import ascii_lowercase, ascii_uppercase, digits


class IRCUser:
    illegal_characters = set(".<>'`()?*#")

    def __init__(self, protocol, username, nickname, realname, host, hostmask, channels, nickattempts, nick_length):
        self.protocol = protocol
        self.__username = username
        self.__nickname = nickname
        self.realname = realname
        self.host = host
        self.__hostmask = hostmask
        self.channels = channels
        self.nickattempts = nickattempts
        self.nick_length = nick_length

    @property
    def hostmask(self):
        return self.__hostmask

    @hostmask.setter
    def hostmask(self, nickname):
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

    @username.setter
    def username(self, params):
        illegal_characters = set(".<>'`()")
        username = params[0]
        username_length = len(username)
        realname = params[3]

        if self.__username is not None:
            raise AttributeError("Client already has a username.")
        if username_length == 0:
            raise ValueError("Username can not be blank.")
        if username_length > self.nick_length:
            raise ValueError("Username can not be greater than {} characters.".format(str(self.nick_length)))
        if any((c in illegal_characters) for c in username):
            raise ValueError("Illegal characters in username.")

        self.__username = username
        self.realname = realname

    @property
    def nickname(self):
        return self.__nickname

    def set_nickname(self, desired_nickname):
        output = None
        if self.hostmask is None:
            self.hostmask = desired_nickname

        if desired_nickname == self.nickname:
            return

        in_use_nicknames = [x.nickname for x in self.protocol.users]

        if desired_nickname in in_use_nicknames:
            # The user instance has no nickname. This is the case on initial connection.
            if self.nickname is None:
                # They've had 2 attempts at changing it - Generate one for them.
                if self.nickattempts != 2:
                    self.nickattempts += 1
                    return ":{} 433 * {} :Nickname is already in use/is not allowed".format(
                        self.host, desired_nickname)
                else:
                    self.rename_to_random_nick(in_use_nicknames)
                    return "Nickname attempts exceeded(2). A random nickname was generated for you."
            else:
                # The user already has a nick, so just send a line telling them its in use and keep things the same.
                return "The nickname {} is already in use/is not allowed.".format(desired_nickname)

        # ToDo: Can this be made the same as the one below?
        if len(desired_nickname) > self.nick_length:
            error = "Error: Nickname exceeded max char limit ({})".format(str(self.nick_length))
            if self.__nickname is None:
                error += " Use /nick to set a new nick."
            return error

        if any((c in self.illegal_characters) for c in desired_nickname):
            error = ":{} 436 * {} :Erroneous Nickname ".format(self.host, desired_nickname)
            if self.nickname is None:
                self.nickattempts += 1
                error += ":{} 432 * {} :Erroneous Nickname ".format(self.host, self.nickname)
            return error

        if self.nickname is not None or self.nickattempts != 0:  # They are renaming themselves.
            if self.channels is not None:  # Send rename notice to any channels they're in
                for connected_channel in self.channels:
                    connected_channel.rename_user(self, desired_nickname)
            if self.nickattempts != 0 and self.nickname is None:  # This nickname is valid
                self.nickattempts = 0  # so set nickattempts to 0
            output = ":{} NICK {}".format(self.hostmask, desired_nickname)  # Tell them it was accepted.

        self.__nickname = desired_nickname
        self.hostmask = desired_nickname
        return output  # Return any errors/any rename notices.

    def rename_to_random_nick(self, current_nicknames):
        protocol_instance_string = str(self.protocol).replace(" ", "")
        random_nick = ''.join(sample(protocol_instance_string, len(protocol_instance_string)))
        random_nick_s = ''.join([c for c in random_nick[:self.nick_length] if c not in self.illegal_characters])

        def validate_nick(nick, current_nicks):
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
        self.__nickname = random_nick_s

