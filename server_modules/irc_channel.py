from enum import Enum


class QuitReason(Enum):
        LEFT = ":{} PART {}\r\n"
        DISCONNECTED = ":{} QUIT :{}\r\n"
        TIMEOUT = ":{} QUIT :{}\r\n"
        UNSPECIFIED = ":{} QUIT :{}\r\n"


class IRCChannel:
    """ Represent channels on the server and implement methods for handling them and participants. """
    def __init__(self, name):
        self.channel_name = name
        self.channel_owner = None
        self.users = []
        self.channel_modes = []
        self.channel_owner_account = []

    def __str__(self):
        host_list = [x.hostmask for x in self.users]
        return "ChannelOwner: {}\nChannelOperators: {}\nChannelName: {}\nHostMaskList: {}\nNickList: {}\n".format(
            self.channel_owner, None, self.channel_name, host_list, self.get_nicknames()
        )  # ToDo: ChannelOperators in __str__

    def add_user(self, user):
        """ Map a user to the channel, send a JOIN notice to everyone currently in it. """
        # This user is already in the channel
        if user in self.users:
            return

        if user.hostmask is None:
            user.set_hostmask(user.nickname)

        user.protocol.join(user.hostmask, self.channel_name)
        user.channels.append(self)
        self.users.append(user)
        for user_ in self.users:
            if user_ != user:
                user_.protocol.sendLine(":{} JOIN :{}".format(user.hostmask, self.channel_name))
        self.send_names(user)

    def remove_user(self, user, leave_message, reason=QuitReason.UNSPECIFIED):
        """ Unmap a user instance from the channel and broadcast the reason. """
        if reason.value == QuitReason.LEFT.value:
            if leave_message is None:
                leave_message = "{} :User Left Channel.".format(self.channel_name)
            else:
                leave_message = "{} :{}".format(self.channel_name, leave_message)
        elif reason.value == QuitReason.DISCONNECTED.value:
            if leave_message is None:
                leave_message = "User Quit Network."
        elif reason.value == QuitReason.TIMEOUT.value:
            if leave_message is None:
                leave_message = "User Timed Out."
        else:
            leave_message = "Unspecified Reason."
        if user is self.channel_owner:
            self.channel_owner = None

        self.broadcast_line(reason.value.format(user.hostmask, leave_message))
        self.users.remove(user)
        user.channels.remove(self)

    def get_nicknames(self):
        """ Get all the nicknames of the currently participating users in the channel. """
        return [x.nickname for x in self.users]

    def who(self, user, server_host):
        """ Return information about the channel to the caller. Used for WHO commands. """
        member_info = []
        if user.nickname not in self.get_nicknames():
            return
        for _user in self.users:  # ToDo: Don't hardcode the hopcount
            member_info.append((
                _user.username, _user.hostmask, server_host, _user.nickname, _user.status, 0, _user.realname
            ))
        return member_info

    def login_owner(self, name, password, user):
        """
        Attempt to map a user as an owner. If the channel currently has someone set as an owner/the person
        issuing the command isn't in the channel, return error.
        """
        if user.nickname not in self.get_nicknames():
            return user.rplhelper.err_noprivileges("You must be on the channel to login as the owner.")
        if name != self.channel_owner_account[0] or password != self.channel_owner_account[1]:
            return user.rplhelper.err_passwordmismatch()
        elif self.channel_owner is not None:
            return user.rplhelper.err_noprivileges("Channel already has an acting owner.")
        else:
            self.channel_owner = user
            return "You have logged in as the channel owner of {}".format(self.channel_name)

    def send_names(self, user):
        """ Sends the nicknames of users currently participating in the channel to the target user. """
        user.protocol.names(user.nickname, self.channel_name, self.get_nicknames())

    def rename_user(self, user, new_nick):
        """ When a user is renamed, update the names list and send a notice to everyone in the channel. """
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

    def broadcast_notice(self, message):
        for user in self.users:
            user.notice(message)
