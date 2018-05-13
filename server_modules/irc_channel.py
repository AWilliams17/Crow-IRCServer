
class IRCChannel:
    def __init__(self, name):
        self.channel_name = name
        # the user list maps user information to a username:
        # 0 = irc_protocol instance,
        # 1 = username,
        # 2 = nickname,
        # 3 = realname,
        # 4 = host,
        # 5 = hostmask
        # 6 = a list of channels the user is in
        self.users = []
