
class IRCChannel:
    def __init__(self, name):
        self.channel_name = name
        self.users = []
        self.usernames = []
        self.nicknames = []
