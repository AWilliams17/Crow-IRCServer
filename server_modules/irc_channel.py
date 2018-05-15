from enum import Enum
# http://riivo.talviste.ee/irc/rfc/index.php?page=command.php&cid=8
# ToDo: Kick, Kicked Methods + Reasons
# ToDo: Implement invite list
# ToDo: Implement Bans + Reasons
# ToDo: Implement passwords
# ToDo: Send topic in add_user (self.topic(self.username, self.channels[channel].channel_name, topic="Test"))
# ToDo: Max Clients
# ToDo: Allow the owner of the channel to delete it


# Is there a better way to go about this?
class QuitReason(Enum):
        LEFT = ":{} QUIT :User Left Channel\r\n"
        DISCONNECTED = ":{} QUIT :User Disconnected\r\n"
        TIMEOUT = ":{} QUIT :User Timed Out\r\n"
        UNSPECIFIED = ":{} QUIT :Unspecified Reason\r\n"


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
            return

        user.protocol.join(user.hostmask, self.channel_name)
        user.channels.append(self)
        self.channel_nicks.append(user.nickname)
        self.users.append(user)
        for user_ in self.users:
            if user_ != user:
                user_.protocol.sendLine(":{} JOIN :{}".format(user.hostmask, self.channel_name))
        self.send_names(user)

    def remove_user(self, user, reason=QuitReason.UNSPECIFIED):
        self.send_line(reason.value.format(user.hostmask))
        self.channel_nicks.remove(user.nickname)
        self.users.remove(user)
        user.channels.remove(self)

    def send_names(self, user):
        user.protocol.names(user.nickname, self.channel_name, self.channel_nicks)

    def rename_user(self, user, new_nick):
        self.channel_nicks.remove(user.nickname)
        self.channel_nicks.append(new_nick)
        for user_ in self.users:
            if user_.protocol is not user:
                user_.protocol.sendLine(":{} NICK {}".format(user.hostmask, new_nick))

    def send_message(self, message, sender):
        for user in self.users:
            if user.hostmask != sender:
                user.protocol.privmsg(sender, self.channel_name, message)

    def send_line(self, line):
        for user in self.users:
            user.protocol.sendLine(line)
