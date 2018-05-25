What I'm doing now:
-Max Clients

General:
-Create setup.py
-Save current rooms + their operators to file and load it on launch
-add logging
-ensure RFC compliance
-implement unimplemented commands in commands.md
-implement ISUPPORT (twisted's irc.py has something for this?) http://www.irc.org/tech_docs/005.html
-implement WHOWAS
-if a user is an operator, add a * next to their nick in WHOIS/WHO
-if a user is a channel operator, add an @ next to their nick in WHOIS/WHO
-make the welcome text include nicks better
-implement MOTD

irc_protocol.py:
-Implement no oper host
-Implement CAP
-Implement max clients
-Implement ACTION
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
