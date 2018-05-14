class IRCUser:
    def __init__(self, protocol, username, nickname, realname, host, hostmask, channels, nickattempts):
        self.protocol = protocol
        self.username = username
        self.nickname = nickname
        self.realname = realname
        self.host = host
        self.hostmask = hostmask
        self.channels = channels
        self.nickattempts = nickattempts
