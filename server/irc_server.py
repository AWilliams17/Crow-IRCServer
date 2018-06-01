from twisted.internet.protocol import Factory
from server.irc_protocol import IRCProtocol
from server.irc_ratelimiter import RateLimiter
from server.irc_clientlimiter import ClientLimiter
from server.irc_ping_manager import PingManager
from server.irc_channelmanager import ChannelManager
from collections import OrderedDict


class ChatServer(Factory):
    def __init__(self, config):
        self.config = config
        self.users = OrderedDict()
        self.channels = OrderedDict()
        self.ratelimiter = RateLimiter()
        self.clientlimiter = ClientLimiter()
        self.pingmanager = PingManager(self.users)
        self.channelmanager = ChannelManager(self.channels, self.config.MaintenanceSettings.ChannelUltimatum)

    def maintenance_delete_old_channels(self):
        """ This method gets called every x amount of days as defined in crow.ini. The purpose of it is to DELETE
        channels which have not had someone login to the owner account for the past y amount of days. """
        self.channelmanager.channel_maintenance()

    def maintenance_ratelimiter(self):
        """ Clear old entries in the ratelimiter dictionary. """
        self.ratelimiter.maintenance()

    def maintenance_flush_server(self):
        """ This method gets called every x minutes as defined in crow.ini The purpose of it is to save current
        channels and their modes, owner details, oper details, and banlists to the server which will be reloaded on
        server restart. """
        pass

    def do_pings(self):
        self.pingmanager.ping_users()

    def buildProtocol(self, addr):
        return IRCProtocol(self.users, self.channels, self.config, self.ratelimiter,
                           self.clientlimiter, self.pingmanager, self.channelmanager)
