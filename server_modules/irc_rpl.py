from twisted.words.protocols.irc import ERR_NOSUCHNICK, ERR_NOSUCHCHANNEL, ERR_UNKNOWNCOMMAND, ERR_UNKNOWNMODE, \
    ERR_NICKNAMEINUSE, ERR_NEEDMOREPARAMS, RPL_YOUREOPER, ERR_PASSWDMISMATCH, ERR_ERRONEUSNICKNAME, \
    ERR_USERSDONTMATCH, ERR_NOPRIVILEGES, ERR_BADCHANMASK, ERR_CANNOTSENDTOCHAN, ERR_NONICKNAMEGIVEN, \
    ERR_NOTONCHANNEL, RPL_AWAY, RPL_UNAWAY, RPL_UMODEIS


class RPLHelper:
    def __init__(self, server_hostname, user_nickname, user_hostmask):
        self.server_hostname = server_hostname
        self.user_nickname = user_nickname
        self.user_hostmask = user_hostmask

    def rpl_youreoper(self):
        return ":{} {} {} :You are now an IRC operator".format(self.server_hostname, RPL_YOUREOPER, self.user_nickname)

    def rpl_away(self):
        return ":{} {} :You are now marked as being away".format(self.user_hostmask, RPL_AWAY)

    def rpl_unaway(self):
        return ":{} {} :You are no longer marked as being away".format(self.user_hostmask, RPL_UNAWAY)

    def rpl_umodeis(self, nick, modes):
        """
        :param nick: The nick of the user who's modes are being checked
        :param modes: A list of the user's modes
        """
        return ":{} {} {} :{}'s modes are: +{}".format(
            self.server_hostname, RPL_UMODEIS, self.user_nickname, nick, modes
        )

    def err_notonchannel(self, description):
        """
        :param description: Describe why this was returned.
        """
        return ":{} {} {} :{}".format(self.server_hostname, ERR_NOTONCHANNEL, self.user_nickname, description)

    def err_nonicknamegiven(self, description):
        """
        :param description: Describe why this was returned.
        """
        return ":{} {} :{}".format(self.server_hostname, ERR_NONICKNAMEGIVEN, description)


    def err_badchanmask(self, destination):
        """
        :param destination: The channel name which has a bad mask.
        """
        return ":{} {} {} {} :No wildcards in destination..".format(
            self.server_hostname, ERR_BADCHANMASK, self.user_nickname, destination
        )

    def err_cannotsendtochan(self, destination, reason):
        """
        :param destination: The channel which couldn't be sent to.
        :param reason: Why it couldn't be sent to.
        """
        return ":{} {} {} {} :{}".format(
            self.server_hostname, ERR_CANNOTSENDTOCHAN, self.user_nickname, destination, reason
        )

    def err_nosuchnick(self, requested_nickname):
        """
        :param requested_nickname: The nickname which was not found.
        """
        return ":{} {} {} {} :No such nick".format(
            self.server_hostname, ERR_NOSUCHNICK, self.user_nickname, requested_nickname
        )

    def err_nosuchchannel(self, requested_channel):
        """
        :param requested_channel: The channel which was not found.
        """
        return ":{} {} {} {} :No such channel".format(
            self.server_hostname, ERR_NOSUCHCHANNEL, self.user_nickname, requested_channel
        )

    def err_unknowncommand(self, command):
        """
        :param command: The command that triggered the error.
        """
        return ":{} {} {} {} :Unknown Command".format(
            self.server_hostname, ERR_UNKNOWNCOMMAND, self.user_nickname, command
        )

    def err_needmoreparams(self, command):
        """
        :param command: The command in need of more parameters.
        """
        return ":{} {} {} {} :Not enough parameters".format(
            self.server_hostname, ERR_NEEDMOREPARAMS, self.user_nickname, command
        )

    def err_passwordmismatch(self):
        return ":{} {} {} :Password Incorrect".format(self.server_hostname, ERR_PASSWDMISMATCH, self.user_nickname)

    def err_erroneousnickname(self, bad_nickname, error_desc):
        """
        :param bad_nickname: The nickname which triggered this error.
        :param error_desc: Description on why the nickname is erroneous.
        """
        return ":{} {} * {} :{}".format(self.server_hostname, ERR_ERRONEUSNICKNAME, bad_nickname, error_desc)

    def err_nicknameinuse(self, inuse_nickname):
        """
        :param inuse_nickname: The nickname which is in use.
        """
        return ":{} {} * {} :Nickname is already in use".format(self.server_hostname, ERR_NICKNAMEINUSE, inuse_nickname)

    def err_unknownmode(self, mode):
        """
        :param mode: The mode which was not found.
        """
        return ":{} {} {} :{} - Unknown Mode".format(self.server_hostname, ERR_UNKNOWNMODE, self.user_nickname, mode)

    def err_usersdontmatach(self, mode):
        """
        :param mode: The attempted mode.
        """
        return ":{} {} {} {} :Cant change mode for other users".format(
            self.server_hostname, ERR_USERSDONTMATCH, self.user_nickname, mode
        )

    def err_noprivileges(self, error="You're not an IRC operator"):
        """
        :param error: Optionally, explain why this was returned.
        :param command: The command which requires elevated privileges.
        """
        return ":{} {} {} :Permission Denied - {}".format(
            self.server_hostname, ERR_NOPRIVILEGES, self.user_nickname, error
        )

