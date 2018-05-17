from random import sample, choice
from string import ascii_lowercase, ascii_uppercase, digits


class IRCUser:
    def __init__(self, protocol, username, nickname, realname, host, hostmask, channels, nickattempts):
        self.protocol = protocol
        self.__username = username
        self.__nickname = nickname
        self.realname = realname
        self.host = host
        self.__hostmask = hostmask
        self.channels = channels
        self.nickattempts = nickattempts

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
        if username_length > 35:
            raise ValueError("Username can not be greater than 35 characters.")
        if any((c in illegal_characters) for c in username):
            raise ValueError("Illegal characters in username.")
        self.__username = username
        self.realname = realname


    @property
    def nickname(self):
        return self.__nickname

    @nickname.setter
    def nickname(self, desired_nickname):
        illegal_characters = set(".<>'`()")

        error = None
        if len(desired_nickname) > 35:
            error = "Error: Nickname exceeded max char limit (35)"
            if self.__nickname is None:
                error = error + " Use /nick to set a new nick."
        if any((c in illegal_characters) for c in desired_nickname):
            error = ":{} 436 * {} :Erroneous Nickname ".format(self.host, desired_nickname)
            if self.nickname is None:
                error = ":{} 432 * {} :Erroneous Nickname ".format(self.host, self.nickname)
                self.nickattempts += 1

        if error is not None:
            raise ValueError(error)

        if self.__nickname is not None:
            if self.channels is not None:
                for connected_channel in self.channels:
                    connected_channel.rename_user(self, desired_nickname)
            self.protocol.sendLine(":{} NICK {}".format(self.hostmask, desired_nickname))

        if self.nickattempts != 0:
            if self.__nickname is not None:
                self.nickattempts = 0
            self.protocol.sendLine(":{} NICK {}".format(self.hostmask, desired_nickname))

        self.__nickname = desired_nickname
        self.hostmask = desired_nickname

    def rename_to_random_nick(self, current_nicknames):
        protocol_instance_string = str(self.protocol).replace(" ", "")
        random_nick = ''.join(sample(protocol_instance_string, len(protocol_instance_string)))
        random_nick_s = ''.join([c for c in random_nick[:35] if c not in set(".<>'`()")])

        def validate_nick(nick, current_nicks):
            if nick in current_nicknames:
                def generate_junk(amount):
                    return ''.join([
                        choice(
                            ascii_lowercase +
                            ascii_uppercase +
                            digits) for i in range(amount)
                    ])

                # Re shuffle the string + Add random garbage to it and then re-validate it, keep it under 35
                nick = (''.join(sample(nick, len(nick))) + generate_junk(15))[:35]
                validate_nick(nick, current_nicks)
            return nick

        random_nick_s = validate_nick(random_nick_s, current_nicknames)
        self.nickname = random_nick_s

