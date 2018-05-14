class IRCChannel:
    def __init__(self, name):
        self.channel_name = name
        self.users = []
        self.channel_nicks = []

    def add_user(self, user):
        if user in self.users:
            return

        if user.nickname is None:
            user.protocol.sendLine("Failed to join channel: Your nickname is not set.")

        user.protocol.join(user.hostmask, self.channel_name)
        user.channels.append(self)
        self.channel_nicks.append(user.nickname)
        self.users.append(user)
        self.send_names()

    def remove_user(self, user):
        self.channel_nicks.remove(user.nickname)
        self.users.remove(user)
        user.channels.remove(self)
        self.send_names()

    def send_names(self):
        for user in self.users:
            user.protocol.names(user.nickname, self.channel_name, self.channel_nicks)

    def send_message(self, message, sender):
        for user in self.users:
            if user.hostmask != sender:
                user.protocol.privmsg(sender, self.channel_name, message)
