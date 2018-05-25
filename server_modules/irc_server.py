from twisted.internet.protocol import Factory
from server_modules.irc_protocol import IRCProtocol
from server_modules.irc_ratelimiter import RateLimiter
from server_modules.irc_clientlimiter import ClientLimiter
from collections import OrderedDict


class ChatServer(Factory):
    def __init__(self, config):
        self.users = OrderedDict()
        self.channels = OrderedDict()
        self.ratelimiter = RateLimiter()
        self.clientlimiter = ClientLimiter()
        self.config = config

    def maintenance_delete_old_channels(self):
        """ This method gets called every x amount of days as defined in crow.ini. The purpose of it is to DELETE
        channels which have not had more than 2 users on it in the past x amount of days."""
        pass
        # self.delete_old_channels()

    def maintenance_ratelimiter(self):
        """ Clear old entries in the ratelimiter dictionary. """
        self.ratelimiter.maintenance()

    def maintenance_flush_server(self):
        """ This method gets called every x minutes as defined in crow.ini The purpose of it is to save current
        channels and their modes, owner details, oper details, and banlists to the server which will be reloaded on
        server restart. """
        pass

    def maintenance_ping(self):
        pass

    def buildProtocol(self, addr):
        return IRCProtocol(self.users, self.channels, self.config, self.ratelimiter, self.clientlimiter)
