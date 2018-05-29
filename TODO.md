A (semi incomplete) list of things currently implemented/unimplemented. will definitely be adding additions.
## General:
* Server Operators [x]
* Server Bans[]
* Server Kicks[]
* TLS[]
* IPV6(?)[]
* TCP6(?)[]
* Ping everyone after a certain amount of time and kick those that haven't responded by the next ping[x]
* Scan and delete/warn inactive channels[x]
* Save current server details (channels, banlists, etc)[]
* Load server details previously saved on server restart[]
* Server restart command for Server OPs[]
* Setup.py[]
* Logging[]
* MOTD[]
* Server Title[x]
* Server Welcome[x]
* Server Description[x]
* ISUPPORT[]
* CAP[]
* CTCPs[]

## Channels:
* Owners[x]
* Expiration[x]
* Operators[]
* Change/Set/Lookup Modes[x]
* Invites[]
* Deletion[x] (Deletion works by expiration - still need to let owners delete their own channel)
* Anti-Spam[] (to be a mode)
* Topics[]
* Bans[]
* Kicks[]
* Mutes[]
* Hash Owner + Oper passwords instead of using plaintext[]
* NOOPERHOST[]

## Users:
* Join channels[x]
* Change nicknames[x]
* Random Nick Generation after 3 failed nick change attempts during initial connection[x]
* Message Channels + Users[x]
* Nickname Registering[]
* Max registered nicks[]
* Change/Set/Lookup Modes[x]
* Leave/Disconnect[x]
* Leave/Disconnect Messages[x]
* WHO[x]
* WHOIS[x]
* WHOWAS[]
* MaxUsernameLength[x]
* MaxNicknameLength[x]
* MaxClients[x]
* If user is a server operator, add a * next to their nick in WHOIS/WHO[]
* If a user is a channel operator, add an @ next to their nick in WHOIS/WHO[]

## Commands (Unimplemented/implemented custom commands + their usage in commands.MD)
* Unknown Command error[x]
* Minimum parameter enforcement[x]
* Rate limits[x]

## MODES
### User Modes:
* 'o' - server operator[x]
* 'D' - disable private messages[]
* 'i' - hide from who and names + online time in whois + what channels user is in[]
* 'z' - connected via tls[]
* 'W' - see when someone does a WHOIS on you[]
* 'R' - using a registered nick[]
# ## Channel Modes:
* 'S' - slow flood[]
* 'I' - invite only[]
* 'P' - passworded[]
More to be decided...
