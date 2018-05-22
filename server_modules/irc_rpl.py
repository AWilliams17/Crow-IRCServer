from twisted.words.protocols.irc import ERR_NOSUCHNICK, ERR_NOSUCHCHANNEL, ERR_UNKNOWNCOMMAND, ERR_UNKNOWNMODE, \
    ERR_NICKNAMEINUSE, ERR_NEEDMOREPARAMS, RPL_YOUREOPER, ERR_PASSWDMISMATCH, ERR_ERRONEUSNICKNAME, \
    ERR_USERSDONTMATCH, ERR_NOPRIVILEGES, ERR_BADCHANMASK, ERR_CANNOTSENDTOCHAN, ERR_NONICKNAMEGIVEN, \
    ERR_NOTONCHANNEL, RPL_UNAWAY, RPL_UMODEIS, RPL_NOWAWAY


class RPLHelper:
    """
    This class is for implemented RPL/ERR responses for a user to receive.
    Every user instance has an RPLHelper instance which generates responses
    for him.

    This is probably very unnecessary but it works fine, and it's
    pretty helpful for common err responses, so I'll keep it.
    """
    def __init__(self, user_instance):
        self.user_instance = user_instance

    def rpl_youreoper(self):
        return ":{} {} {} :You are now an IRC operator".format(
            self.user_instance.server_host, RPL_YOUREOPER, self.user_instance.nickname
        )

    def rpl_nowaway(self):
        return ":{} {} {} :You are now marked as being away".format(
            self.user_instance.server_host, RPL_NOWAWAY, self.user_instance.nickname
        )

    def rpl_unaway(self):
        return ":{} {} {} :You are no longer marked as being away".format(
            self.user_instance.server_host, RPL_UNAWAY, self.user_instance.nickname
        )

    def rpl_umodeis(self, nick, modes):
        """
        :param nick: The nick of the user who's modes are being checked
        :param modes: A list of the user's modes
        """
        return ":{} {} {} :{}'s modes are: +{}".format(
            self.user_instance.server_host, RPL_UMODEIS, self.user_instance.nickname, nick, modes
        )

    def err_notonchannel(self, description):
        """
        :param description: Describe why this was returned.
        """
        return ":{} {} {} :{}".format(
            self.user_instance.server_host, ERR_NOTONCHANNEL, self.user_instance.nickname, description
        )

    def err_nonicknamegiven(self, description):
        """
        :param description: Describe why this was returned.
        """
        return ":{} {} :{}".format(self.user_instance.server_host, ERR_NONICKNAMEGIVEN, description)

    def err_badchanmask(self, destination):
        """
        :param destination: The channel name which has a bad mask.
        """
        return ":{} {} {} {} :No wildcards in destination..".format(
            self.user_instance.server_host, ERR_BADCHANMASK, self.user_instance.nickname, destination
        )

    def err_cannotsendtochan(self, destination, reason):
        """
        :param destination: The channel which couldn't be sent to.
        :param reason: Why it couldn't be sent to.
        """
        return ":{} {} {} {} :{}".format(
            self.user_instance.server_host, ERR_CANNOTSENDTOCHAN, self.user_instance.nickname, destination, reason
        )

    def err_nosuchnick(self, requested_nickname):
        """
        :param requested_nickname: The nickname which was not found.
        """
        return ":{} {} {} {} :No such nick".format(
            self.user_instance.server_host, ERR_NOSUCHNICK, self.user_instance.nickname, requested_nickname
        )

    def err_nosuchchannel(self, requested_channel):
        """
        :param requested_channel: The channel which was not found.
        """
        return ":{} {} {} {} :No such channel".format(
            self.user_instance.server_host, ERR_NOSUCHCHANNEL, self.user_instance.nickname, requested_channel
        )

    def err_unknowncommand(self, command):
        """
        :param command: The command that triggered the error.
        """
        return ":{} {} {} {} :Unknown Command".format(
            self.user_instance.server_host, ERR_UNKNOWNCOMMAND, self.user_instance.nickname, command
        )

    def err_needmoreparams(self, command):
        """
        :param command: The command in need of more parameters.
        """
        return ":{} {} {} {} :Not enough parameters".format(
            self.user_instance.server_host, ERR_NEEDMOREPARAMS, self.user_instance.nickname, command
        )

    def err_passwordmismatch(self):
        return ":{} {} {} :Password Incorrect".format(
            self.user_instance.server_host, ERR_PASSWDMISMATCH, self.user_instance.nickname
        )

    def err_erroneousnickname(self, bad_nickname, error_desc):
        """
        :param bad_nickname: The nickname which triggered this error.
        :param error_desc: Description on why the nickname is erroneous.
        """
        return ":{} {} * {} :{}".format(self.user_instance.server_host, ERR_ERRONEUSNICKNAME, bad_nickname, error_desc)

    def err_nicknameinuse(self, inuse_nickname):
        """
        :param inuse_nickname: The nickname which is in use.
        """
        return ":{} {} * {} :Nickname is already in use".format(
            self.user_instance.server_host, ERR_NICKNAMEINUSE, inuse_nickname
        )

    def err_unknownmode(self):
        """
        :param mode: The mode which was not found.
        """
        return ":{} {} {} :Unknown Mode".format(
            self.user_instance.server_host, ERR_UNKNOWNMODE, self.user_instance.nickname
        )

    def err_usersdontmatach(self, mode):
        """
        :param mode: The attempted mode.
        """
        return ":{} {} {} {} :Cant change mode for other users".format(
            self.user_instance.server_host, ERR_USERSDONTMATCH, self.user_instance.nickname, mode
        )

    def err_noprivileges(self, error="You're not an IRC operator"):
        """
        :param error: Optionally, explain why this was returned.
        """
        return ":{} {} {} :Permission Denied - {}".format(
            self.user_instance.server_host, ERR_NOPRIVILEGES, self.user_instance.nickname, error
        )

