# Setting up crow.ini
The following serves as a reference for the settings outlined in the `crow.ini` file.
I've tried to make the ini self documenting by making the setting names detailed,
but if you are confused about anything this will hopefully clear things up.


## ServerSettings:
### This section handles the primary details concerning the server itself.
* Port: This is the port the server will listen on. Common IRC ports
are 6667,6668,6669, and 7000, with 6697 being for SSL (not implemented).
The default port of 6667 should suffice.

* Interface: What network interface to bind to. 127.0.0.1 is localhost.
To listen on all interfaces, use 0.0.0.

* PingInterval: How often clients connected to the server should be pinged, in minutes.
Default value is 3. If set to 0, clients will not be pinged. (they won't be timed out.)

* ServerName: The name communicated to the client on initial connection.

* ServerDescription: Describes the server. At the moment it is only used
in WHOIS replies.

* ServerWelcome: The welcome message echoed to the client on initial connection.
The client's nickname is appended to the end of it.

## MaintenanceSettings
### This section handles details pertaining to automated maintenance in the server.
* RateLimitClearInterval: How much time in minutes to wait before clearing old entries
in the rate limiter dictionary. Default is every 5 minutes. If set to 0, then
ratelimiter entries will not be removed. (not recommended)

* (Not Implemented)FlushInterval: How much time in hours to wait before flushing current
server details (current channels + their opers, owner, modes, and banlists) + the server's
own banlist. The default value is 1 hour. NOTE: IF SET TO 0, SERVER DETAILS WILL NOT BE SAVED!

* ChannelScanInterval: How many days to wait before running the old channel scan.
Default value is 1. If the interval is 0, then old channels will not be removed.

* ChannelUltimatum: (If ChannelScanInterval is 0, this value will not be used) This controls
how long a channel must have no owner logged in before being considered for deletion. For example,
if set to 7 days, then when the owner logs out and the channel scan is initiated, then the last
owner login date is compared against this value. If there are less than 3 days left before
the channel is slated for deletion, then a notice will be sent to the channel
every time the channel scan is initiated until there are no days remaining, where it is then
slated for deletion on the next scan. If an owner logs in, then this all of this is reset. Also,
once a channel is slated for deletion on the next scan, if an owner logs in before the scan
occurs, then the channel will be saved.

## UserSettings:
### This section handles details pertaining to users connected to the server.
* MaxUsernameLength: The maximum amount of characters a username can be.

* MaxNicknameLength: The maximum amount of characters a nickname can be.

* MaxClients: How many clients a host can have connected at the same time.

* Operators: A list of operator usernames and their associated passwords. Separate each
username:password pair with a comma. Note, if a username is the same as a previous
username, that previous username will have it's password value replaced by the subsequent
username's associated password.
