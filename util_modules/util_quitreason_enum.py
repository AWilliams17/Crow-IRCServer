from enum import Enum
""" For use in irc_channel for creating a leave message for a user. This module is kinda unneeded."""


class QuitReason(Enum):
        LEFT = ":{} PART {}\r\n"
        DISCONNECTED = ":{} QUIT :{}\r\n"
        TIMEOUT = ":{} QUIT :{}\r\n"
        UNSPECIFIED = ":{} QUIT :{}\r\n"
