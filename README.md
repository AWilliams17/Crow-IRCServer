# Twisted-IRC-server
This is an (incomplete) Python3 Twisted IRC server implementation.

A lot of commands are not implemented yet, but here's a list of things that (mostly) work:  
-Joining Channels (on joining, you are set as the owner, and given the details to log back in
as the channel owner. use /CHOWNER (name) (password) (channel) to log in as channel owner.  
-Messaging channels + other users  
-Modes (at the moment, only the operator flag is implemented, I exists but it does nothing.)  
-Nickname changing  

Things that need implementation:  
-IRC Channel operators  
-CAP functionality  
-A lot more stuff  

The code is kind of a mess right now too.

This started as a fork of d34thh4ck3r's Twisted-IRC-server, but I went ahead
and rewrote it as what currently was written in the fork didn't really work
correctly.

This is the first time I've written a server with Twisted so I imagine
I may have done some things wrong.
