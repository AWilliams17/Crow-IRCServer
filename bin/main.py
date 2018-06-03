from server.irc_config.config import IRCConfig
from server.irc_server import ChatServer
from twisted.internet import reactor, task
from twisted.internet.endpoints import serverFromString
from os import getcwd, path

import twisted.internet.defer
twisted.internet.defer.setDebugging(True)


def setup_loopingcalls(server, maintenance_settings):
	ratelimitclearinterval = maintenance_settings.RateLimitClearInterval * 60
	flushinterval = maintenance_settings.FlushInterval * 3600
	channelscaninterval = maintenance_settings.ChannelScanInterval * 86400
	pinginterval = server_settings.PingInterval * 60

	if ratelimitclearinterval != 0:
		task.LoopingCall(server.maintenance_ratelimiter).start(ratelimitclearinterval)

	if flushinterval != 0:  # not implemented
		task.LoopingCall(server.maintenance_flush_server).start(flushinterval)

	if channelscaninterval != 0:
		task.LoopingCall(server.maintenance_delete_old_channels).start(channelscaninterval)

	if pinginterval != 0:
		task.LoopingCall(server.do_pings).start(pinginterval)


def create_ssl_endpoint(ssl_settings):
	if server_config.SSLSettings.SSLEnabled:
		print("SSLEnabled is True - Attempting to construct an SSL Endpoint...")
		ssl_key = ssl_settings.SSLKeyPath
		ssl_cert = ssl_settings.SSLCertPath
		if ssl_key is not None and ssl_cert is not None:
			ssl_endpoint_out = serverFromString(reactor, "ssl:6697:privateKey={}:certKey={}".format(ssl_key, ssl_cert))
			print("SSL Endpoint was successfully made using keyfile '{}' and cert file '{}'".format(ssl_key, ssl_cert))
			return ssl_endpoint_out
		print("Error making SSL endpoint: SSL key/SSL cert not set.")


def create_endpoint(ports):
	pass


if __name__ == '__main__':
	ini_path = getcwd().strip("bin") + "/crow.ini"
	server_config = IRCConfig(ini_path)
	if not path.exists(ini_path):
		server_config.flush_config()
	config_output = server_config.read_config()
	server_settings = server_config.ServerSettings  # just for convenience

	if config_output is not None:  # config output is not yet implemented so this does nothing
		for output in config_output:
			print(output)

	server_instance = ChatServer(server_config)
	setup_loopingcalls(server_instance, server_config.MaintenanceSettings)

	ssl_endpoint = create_ssl_endpoint(server_config.SSLSettings)
	if ssl_endpoint is not None:
		ssl_endpoint.listen(server_instance)
		print("SSL Endpoint will now be listening on port 6697")

	endpoint = serverFromString(reactor, "tcp:{}:interface={}".format(server_settings.Port, server_settings.Interface))
	endpoint.listen(server_instance)
	reactor.run()
