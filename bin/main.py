from server_modules.irc_server import ChatServer
from server_modules.irc_config import IRCConfig
from util_modules.config_reaper import *
from twisted.internet import reactor, task
from twisted.internet.endpoints import TCP4ServerEndpoint

import twisted.internet.defer
twisted.internet.defer.setDebugging(True)


def setup_loopingcalls(server, maintenance_settings, server_settings):
	ratelimitclearinterval = maintenance_settings.RateLimitClearInterval * 60
	flushinterval = maintenance_settings.FlushInterval * 3600
	channelscaninterval = maintenance_settings.ChannelScanInterval * 86400
	pinginterval = server_settings.PingInterval * 60

	if ratelimitclearinterval != 0:
		task.LoopingCall(server.maintenance_ratelimiter).start(ratelimitclearinterval)

	if flushinterval != 0:
		task.LoopingCall(server.maintenance_flush_server).start(flushinterval)

	if channelscaninterval != 0:
		task.LoopingCall(server.maintenance_delete_old_channels).start(channelscaninterval)

	if pinginterval != 0:
		task.LoopingCall(server.do_pings).start(pinginterval)


if __name__ == '__main__':
	server_config = IRCConfig()
	server_config_parser = ConfigReaper(server_config)
	config_output = server_config_parser.read_config()

	if config_output is not None:
		for output in config_output:
			print(output)

	server_instance = ChatServer(server_config)
	setup_loopingcalls(server_instance, server_config.MaintenanceSettings, server_config.ServerSettings)

	endpoint = TCP4ServerEndpoint(
		reactor, port=server_config.ServerSettings.Port, interface=server_config.ServerSettings.Interface
	)
	endpoint.listen(server_instance)
	reactor.run()
