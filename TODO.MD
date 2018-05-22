General:
-Create setup.py
-Save current rooms + their operators to file and load it on launch
-add logging
-ensure RFC compliance
-implement unimplemented commands in commands.md
-implement ISUPPORT (twisted's irc.py has something for this?)

irc_protocol.py:
-Refactor irc_WHO
-Refactor irc_WHOIS
-Refactor irc_MODE
-Implement no oper host
-Implement CAP
-Implement max clients
-See if PING/PONG is working
-Add more modes

irc_channel.py:
-Implement invite list
-Implement bans + ban reasons
-Implement passwords
-Implement topics
-Implement deletion
-Implement operators
-Implement channel modes
-Test channel owner login more thoroughly

irc_user.py:
-Refactor set_nickname
-Refactor set_mode
