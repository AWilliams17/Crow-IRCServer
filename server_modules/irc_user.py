class IRCUser:
    def __init__(self, protocol, username, nickname, realname, host, hostmask, channels, nickattempts):
        self.protocol = protocol
        self.username = username
        self._nickname = nickname
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
    def nickname(self):
        return self._nickname

    @nickname.setter
    def nickname(self, desired_nickname):
        if len(desired_nickname) > 35:
            raise ValueError("Error: Nickname exceeded max char limit (35).")



