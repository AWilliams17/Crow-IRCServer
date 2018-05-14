class IRCChannel:
    def __init__(self, name):
        self.channel_name = name
        self.users = []
        self.channel_nicks = []

    def add_user(self, user):
        if user in self.users:
            return

        if user["Nickname"] is None:
            user["Protocol"].sendLine("Failed to join channel: Your nickname is not set.")

        user["Protocol"].join(user["Hostmask"], self.channel_name)
        user["Channels"].append(self)
        self.channel_nicks.append(user["Nickname"])
        self.users.append(user)
        self.send_names()

    def remove_user(self, user):
        self.channel_nicks.remove(user["Nickname"])
        self.users.remove(user)
        user["Channels"].remove(self)
        self.send_names()

    def send_names(self):
        for user in self.users:
            user["Protocol"].names(user["Nickname"], self.channel_name, self.channel_nicks)

    def broadcast(self, message):
        for user in self.users:
            user["Protocol"].sendLine(message)

