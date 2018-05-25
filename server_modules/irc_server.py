from twisted.internet.protocol import Factory
from server_modules.irc_protocol import IRCProtocol
from util_modules.util_rate_limiter import RateLimiter
from util_modules.util_client_limiter import ClientLimiter
from collections import OrderedDict


class ChatServer(Factory):
    def __init__(self, config):
        self.users = OrderedDict()
        self.channels = OrderedDict()
        self.ratelimiter = RateLimiter()
        self.clientlimiter = ClientLimiter()
        self.config = config

    def buildProtocol(self, addr):
        return IRCProtocol(self.users, self.channels, self.config, self.ratelimiter, self.clientlimiter)
