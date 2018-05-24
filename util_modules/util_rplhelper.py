from twisted.words.protocols.irc import ERR_NOSUCHNICK, ERR_NOSUCHCHANNEL, ERR_UNKNOWNCOMMAND, ERR_UNKNOWNMODE, \
    ERR_NICKNAMEINUSE, ERR_NEEDMOREPARAMS, RPL_YOUREOPER, ERR_PASSWDMISMATCH, ERR_ERRONEUSNICKNAME, \
    ERR_USERSDONTMATCH, ERR_NOPRIVILEGES, ERR_BADCHANMASK, ERR_CANNOTSENDTOCHAN, ERR_NONICKNAMEGIVEN, \
    ERR_NOTONCHANNEL, RPL_UNAWAY, RPL_UMODEIS, RPL_NOWAWAY, RPL_ENDOFWHO


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
        return ":{} {} {} :{}'s modes are: +{}".format(
            self.user_instance.server_host, RPL_UMODEIS, self.user_instance.nickname, nick, modes
        )

    def rpl_endofwho(self, channel):
        return ":{} 315 {} {} :End of /WHO list.".format(
            self.user_instance.server_host, RPL_ENDOFWHO, self.user_instance.nickname, channel
        )

    def err_notonchannel(self, description):
        return ":{} {} {} :{}".format(
            self.user_instance.server_host, ERR_NOTONCHANNEL, self.user_instance.nickname, description
        )

    def err_nonicknamegiven(self, description):
        return ":{} {} :{}".format(self.user_instance.server_host, ERR_NONICKNAMEGIVEN, description)

    def err_badchanmask(self, destination):
        return ":{} {} {} {} :No wildcards in destination..".format(
            self.user_instance.server_host, ERR_BADCHANMASK, self.user_instance.nickname, destination
        )

    def err_cannotsendtochan(self, destination, reason):
        return ":{} {} {} {} :{}".format(
            self.user_instance.server_host, ERR_CANNOTSENDTOCHAN, self.user_instance.nickname, destination, reason
        )

    def err_nosuchnick(self):
        return ":{} {} {} :No such nick".format(
            self.user_instance.server_host, ERR_NOSUCHNICK, self.user_instance.nickname
        )

    def err_nosuchchannel(self):
        return ":{} {} {} :No such channel".format(
            self.user_instance.server_host, ERR_NOSUCHCHANNEL, self.user_instance.nickname
        )

    def err_unknowncommand(self, command):
        return ":{} {} {} {} :Unknown Command".format(
            self.user_instance.server_host, ERR_UNKNOWNCOMMAND, self.user_instance.nickname, command
        )

    def err_needmoreparams(self, command):
        return ":{} {} {} {} :Not enough parameters".format(
            self.user_instance.server_host, ERR_NEEDMOREPARAMS, self.user_instance.nickname, command
        )

    def err_passwordmismatch(self):
        return ":{} {} {} :Password Incorrect".format(
            self.user_instance.server_host, ERR_PASSWDMISMATCH, self.user_instance.nickname
        )

    def err_erroneousnickname(self, bad_nickname, error_desc):
        return ":{} {} * {} :{}".format(self.user_instance.server_host, ERR_ERRONEUSNICKNAME, bad_nickname, error_desc)

    def err_nicknameinuse(self, inuse_nickname):
        return ":{} {} * {} :Nickname is already in use".format(
            self.user_instance.server_host, ERR_NICKNAMEINUSE, inuse_nickname
        )

    def err_unknownmode(self):
        return ":{} {} {} :Unknown Mode".format(
            self.user_instance.server_host, ERR_UNKNOWNMODE, self.user_instance.nickname
        )

    def err_usersdontmatach(self, mode):
        return ":{} {} {} {} :Cant change mode for other users".format(
            self.user_instance.server_host, ERR_USERSDONTMATCH, self.user_instance.nickname, mode
        )

    def err_noprivileges(self, error="You're not an IRC operator"):
        return ":{} {} {} :Permission Denied - {}".format(
            self.user_instance.server_host, ERR_NOPRIVILEGES, self.user_instance.nickname, error
        )
