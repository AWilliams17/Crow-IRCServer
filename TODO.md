A (semi incomplete) list of things currently implemented/unimplemented. will definitely be adding additions.
## General:
* [x] Server Operators
* [ ] Server Bans
* [ ] Server Kicks
* [X] TLS
* [x] Ping everyone after a certain amount of time and kick those that haven't responded by the next ping
* [x] Scan and delete/warn inactive channels
* [ ] Save current server details (channels, banlists, etc)
* [ ] Load server details previously saved on server restart
* [ ] Setup.py
* [ ] Logging
* [ ] MOTD
* [x] Server Title
* [x] Server Welcome
* [x] Server Description
* [x] Configuration file
* [ ] ISUPPORT
* [ ] CAP
* [ ] CTCPs
* [ ] Server OP alerts
* [ ] Server monitoring console/command for ops
* [ ] ^On that note, have a module, irc_console, with neat formatting things for printing to the console.
* [ ] NickServ/CrowBot (maybe)
* [ ] Store things in a database and not a text file...
* [ ] Set modes on user when they connect. Get the modes to use from the config file.

## Channels:
* [x] Owners
* [x] Expiration
* [X] Operators
* [x] Change/Set/Lookup Modes
* [ ] Invites
* [x] Deletion (Deletion works by expiration - still need to let owners delete their own channel)
* [ ] Anti-Spam (to be a mode)
* [ ] Topics
* [ ] Bans
* [ ] Kicks
* [ ] Mutes
* [ ] Hash Owner + Oper passwords instead of using plaintext
* [ ] NOOPERHOST
* [ ] Sub-Channels (might be a dumb idea)
* [ ] Change Channel Name Command for owners
* [ ] Co-Owners

## Users:
* [x] Join channels
* [x] Change nicknames
* [x] Random Nick Generation after 3 failed nick change attempts during initial connection
* [x] Message Channels + Users
* [ ] Nickname Registering
* [ ] Max registered nicks
* [x] Change/Set/Lookup Modes
* [x] Leave/Disconnect
* [x] Leave/Disconnect Messages
* [x] WHO
* [x] WHOIS
* [ ] WHOWAS
* [x] MaxUsernameLength
* [x] MaxNicknameLength
* [x] MaxClients
* [ ] If user is a server operator, add a * next to their nick in WHOIS/WHO
* [ ] If a user is a channel operator, add an @ next to their nick in WHOIS/WHO

## Commands (Unimplemented/implemented custom commands + their usage in commands.MD)
* [x] Unknown Command error
* [x] Minimum parameter enforcement
* [x] Rate limits
* [ ] ACTION
* [ ] NOTICE
* [ ] Do all the unimplemented commands in commands.MD

## MODES
### User Modes:
* [x] 'o' - server operator
* [ ] 'D' - disable private messages
* [ ] 'i' - hide from who and names + online time in whois + what channels user is in
* [ ] 'z' - connected via tls
* [ ] 'W' - see when someone does a WHOIS on you
* [ ] 'R' - using a registered nick
### Channel Modes:
* [ ] 'S' - slow flood
* [ ] 'I' - invite only
* [ ] 'P' - passworded
More to be decided...
