from enum import Enum


class QuitReason(Enum):
        """ For use in irc_channel for creating a leave message for a user. This module is kinda unneeded. """
        LEFT = ":{} PART {}\r\n"
        DISCONNECTED = ":{} QUIT :{}\r\n"
        TIMEOUT = ":{} QUIT :User Timed Out: {} seconds.\r\n"
        UNSPECIFIED = ":{} QUIT :{}\r\n"
