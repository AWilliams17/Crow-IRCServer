from enum import Enum
# http://riivo.talviste.ee/irc/rfc/index.php?page=command.php&cid=8
# ToDo: Kick, Kicked Methods + Reasons
# ToDo: Implement invite list
# ToDo: Implement Bans + Reasons
# ToDo: Implement passwords
# ToDo: Send topic in add_user (self.topic(self.username, self.channels[channel].channel_name, topic="Test"))
# ToDo: Allow the owner of the channel to delete it


class QuitReason(Enum):
        LEFT = ":{} QUIT :{}\r\n"
        DISCONNECTED = ":{} QUIT :{}\r\n"
        TIMEOUT = ":{} QUIT :{}\r\n"
        UNSPECIFIED = ":{} QUIT :{}\r\n"


class IRCChannel:
    def __init__(self, name):
        self.channel_name = name
        self.users = []
        self.channel_nicks = []

    def __str__(self):
        host_list = [x.hostmask for x in self.users]
        return "ChannelName: {}\nHostMaskList: {}\nNickList: {}\n".format(
            self.channel_name, host_list, self.channel_nicks
        )

    def add_user(self, user):
        # This user is already in the channel
        if user in self.users:
            return

        if user.nickname is None:
            return "Failed to join channel: Your nickname is not set."  # ToDo: 431

        if user.hostmask is None:
            user.set_hostmask(user.nickname)

        user.protocol.join(user.hostmask, self.channel_name)
        user.channels.append(self)
        self.channel_nicks.append(user.nickname)
        self.users.append(user)
        for user_ in self.users:
            if user_ != user:
                user_.protocol.sendLine(":{} JOIN :{}".format(user.hostmask, self.channel_name))
        self.send_names(user)
        return None

    def remove_user(self, user, leave_message, reason=QuitReason.UNSPECIFIED):
        if reason == QuitReason.LEFT.value and leave_message is None:
            leave_message = "User Left Channel."
        elif reason == QuitReason.DISCONNECTED.value and leave_message is None:
            leave_message = "User Quit Network."
        elif reason == QuitReason.TIMEOUT.value:
            leave_message = "User Timed Out."
        elif reason == QuitReason.UNSPECIFIED.value:
            leave_message = "Unspecified Reason."
        self.broadcast_line(reason.value.format(user.hostmask, leave_message))
        self.channel_nicks.remove(user.nickname)
        self.users.remove(user)
        user.channels.remove(self)

    def who(self, user, server_host):
        member_info = []
        if user.nickname not in self.channel_nicks:
            return None
        for _user in self.users:  # ToDo: Don't hardcode the hopcount
            member_info.append((
                _user.username, _user.hostmask, server_host, _user.nickname, _user.status, 0, _user.realname
            ))
        return member_info

    def set_away(self, user, reason):
        message = ":{} AWAY :{}".format(user.hostmask, reason)
        if reason is None:
            message = ":{} AWAY".format(user.hostmask)
        for user_ in self.users:
            user_.protocol.sendLine(message)

    def send_names(self, user):
        user.protocol.names(user.nickname, self.channel_name, self.channel_nicks)

    def rename_user(self, user, new_nick):
        self.channel_nicks.remove(user.nickname)
        self.channel_nicks.append(new_nick)
        for user_ in self.users:
            if user_.protocol is not user:
                user_.protocol.sendLine(":{} NICK {}".format(user.hostmask, new_nick))

    def broadcast_message(self, message, sender):
        for user in self.users:
            if user.hostmask != sender:
                user.protocol.privmsg(sender, self.channel_name, message)

    def broadcast_line(self, line):
        for user in self.users:
            user.protocol.sendLine(line)
