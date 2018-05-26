from util_modules.util_quitreason_enum import QuitReason
from time import time


class IRCChannel:
    """ Represent channels on the server and implement methods for handling them and participants. """
    def __init__(self, name, channelmanager):
        self.channel_name = name
        self.channel_owner = None
        self.last_owner_login = None
        self.scheduled_for_deletion = False
        self.deleted = False
        self.users = []
        self.channel_modes = []
        self.channel_owner_account = []
        self.channel_manager = channelmanager

    def __str__(self):
        host_list = [x.hostmask for x in self.users]
        return "ChannelOwner: {}\nChannelOperators: {}\nChannelName: {}\nHostMaskList: {}\nNickList: {}\n".format(
            self.channel_owner, None, self.channel_name, host_list, self.get_nicknames()
        )  # ToDo: ChannelOperators in __str__

    def add_user(self, user):
        """ Map a user to the channel, send a JOIN notice to everyone currently in it. """
        # This user is already in the channel
        if self.deleted:
            user.protocol.sendLine(
                "The channel is being deleted. "
                "\nWait a moment and try again to create a new channel with it's name."
            )
        if user in self.users:
            return

        user.protocol.join(user.hostmask, self.channel_name)
        user.channels.append(self)
        self.users.append(user)
        join_rpl = ":{} JOIN :{}".format(user.hostmask, self.channel_name)
        [x.protocol.sendLine(join_rpl) for x in self.users if x is not user]
        self.send_names(user)

    def remove_user(self, user, leave_message, reason=QuitReason.UNSPECIFIED, timeout_seconds=None):
        """ Unmap a user instance from the channel and broadcast the reason. """
        if reason.value == QuitReason.LEFT.value:
            if leave_message is None:
                leave_message = "{} :User Left Channel.".format(self.channel_name)
            else:
                leave_message = "{} :{}".format(self.channel_name, leave_message)
        elif reason.value == QuitReason.DISCONNECTED.value:
            if leave_message is None:
                leave_message = "User Quit Network."
        elif reason.value == QuitReason.TIMEOUT.value and timeout_seconds is not None:
            leave_message = timeout_seconds
        else:
            leave_message = "Unspecified Reason."
        if user is self.channel_owner:
            self.channel_owner = None
            self.last_owner_login = time()  # So it won't be deleted if the owner logged in 7 days ago and never
            # logged out, thus never resetting the last owner login time to something that would prevent deletion.

        self.users.remove(user)
        self.broadcast_line(reason.value.format(user.hostmask, leave_message))
        user.channels.remove(self)

    def get_nicknames(self):
        """ Get all the nicknames of the currently participating users in the channel. """
        return [x.nickname for x in self.users]

    def who(self, user, server_host):
        """ Return information about the channel to the caller. Used for WHO commands. """
        if user.nickname not in self.get_nicknames():
            return user.rplhelper.err_notonchannel("You must be on the channel to perform a /who")
        return [tuple([x.username, x.hostmask, server_host, x.nickname, x.status, 0, x.realname]) for x in self.users]

    def login_owner(self, name, password, user):
        """
        Attempt to map a user as an owner. If the channel currently has someone set as an owner/the person
        issuing the command isn't in the channel, return error.
        """
        if user.nickname not in self.get_nicknames():
            return user.rplhelper.err_noprivileges("You must be on the channel to login as the owner.")
        elif name != self.channel_owner_account[0] or password != self.channel_owner_account[1]:
            return user.rplhelper.err_passwordmismatch()
        elif self.channel_owner is not None:
            return user.rplhelper.err_noprivileges("Channel already has an acting owner.")
        else:
            self.channel_owner = user
            self.last_owner_login = int(time())
            if self.scheduled_for_deletion:
                pass  # ToDo: Tell everyone channel will not be deleted.
            self.scheduled_for_deletion = False
            return "You have logged in as the channel owner of {}".format(self.channel_name)

    def send_names(self, user):
        """ Sends the nicknames of users currently participating in the channel to the target user. """
        user.protocol.names(user.nickname, self.channel_name, self.get_nicknames())

    def rename_user(self, user, new_nick):
        """ When a user is renamed, update the names list and send a notice to everyone in the channel. """
        for user_ in self.users:
            if user_.protocol is not user:
                user_.protocol.sendLine(":{} NICK {}".format(user.hostmask, new_nick))

    def get_modes(self):
        return "getting channel modes not implemented"  # ToDo

    def set_mode(self):
        return "setting channel modes not implemented"  # ToDo

    def delete_channel(self):
        self.channel_manager.delete_channel(self)

    def broadcast_message(self, message, sender):
        for user in self.users:
            if user.hostmask != sender:
                user.protocol.privmsg(sender, self.channel_name, message)
        self.delete_channel()

    def broadcast_line(self, line):
        for user in self.users:
            user.protocol.sendLine(line)

    def broadcast_notice(self, notice):
        for user in self.users:
            notice_line = ":{} NOTICE {} :{}".format(user.hostmask, self.channel_name, notice)
            user.protocol.sendLine(notice_line)

