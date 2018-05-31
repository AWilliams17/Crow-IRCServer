from server_modules.irc_config import IRCConfig
from twisted.internet import reactor, task
from os import getcwd, path

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
	ini_path = getcwd().strip("bin") + "/crow.ini"
	server_config = IRCConfig(ini_path)
	if not path.exists(ini_path):
		server_config.flush_config()
	server_config.read_config()

	#if config_output is not None:
	#	for output in config_output:
	#		print(output)

	#server_instance = ChatServer(server_config)
	#setup_loopingcalls(server_instance, server_config.MaintenanceSettings, server_config.ServerSettings)

	#endpoint = TCP4ServerEndpoint(
	#	reactor, port=server_config.ServerSettings.Port, interface=server_config.ServerSettings.Interface
	#)
	#endpoint.listen(server_instance)
	#reactor.run()
