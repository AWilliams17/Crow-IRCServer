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

    def do_maintenance(self):
        """ This method gets called every x minutes as defined in crow.ini, so any maintenance methods called here will
         be called. """
        self.ratelimiter.maintenance()
        # self.delete_old_channels() - ToDo: if specified in config, delete old channels.
        # (channels which have not had anyone on them, including owner in atleast a week)

    def flush_server(self):
        """ This method gets called every 30 minutes (hard coded). The purpose of it is to save current channels and
        their modes, owner details, oper details, and banlists to the server which will be reloaded on
        server restart. """
        pass

    def buildProtocol(self, addr):
        return IRCProtocol(self.users, self.channels, self.config, self.ratelimiter, self.clientlimiter)
