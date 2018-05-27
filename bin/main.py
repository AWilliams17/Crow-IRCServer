from server_modules.irc_server import ChatServer
from server_modules.irc_config import IRCConfig
from util_modules.config_reaper import *
from twisted.internet import reactor, task
from twisted.internet.endpoints import TCP4ServerEndpoint

import twisted.internet.defer
twisted.internet.defer.setDebugging(True)


def setup_loopingcalls(server, maintenance_settings, server_settings):
	ratelimitclearinterval = maintenance_settings["RateLimitClearInterval"] * 60
	flushinterval = maintenance_settings["FlushInterval"] * 3600
	channelscaninterval = maintenance_settings["ChannelScanInterval"] * 86400
	pinginterval = server_settings["PingInterval"] * 60

	if ratelimitclearinterval != 0:
		task.LoopingCall(server.maintenance_ratelimiter).start(ratelimitclearinterval)

	if flushinterval != 0:
		task.LoopingCall(server.maintenance_flush_server).start(flushinterval)

	if channelscaninterval != 0:
		task.LoopingCall(server.maintenance_delete_old_channels).start(channelscaninterval)

	if pinginterval != 0:
		task.LoopingCall(server.do_pings).start(pinginterval)


if __name__ == '__main__':
	try:
		server_config = IRCConfig()
		server_config_parser = ConfigReaper(server_config)
		server_config_parser.read_config()

		"""
		server_port = server_config.ServerSettings['Port']
		server_interface = server_config.ServerSettings['Interface']
		server_instance = ChatServer(server_config)
		setup_loopingcalls(server_instance, server_config.MaintenanceSettings, server_config.ServerSettings)

		endpoint = TCP4ServerEndpoint(reactor, port=server_port, interface=server_interface)
		endpoint.listen(server_instance)
		reactor.run()
		"""
	except Exception as e:
		print("Exception Triggered: {}".format(e))
		exit()
