from server.irc_config.config import IRCConfig
from server.irc_server import ChatServer
from twisted.internet import reactor, task
from twisted.internet.endpoints import serverFromString
from os import getcwd, path, getuid


import twisted.internet.defer
twisted.internet.defer.setDebugging(True)


def setup_loopingcalls(server, server_settings, maintenance_settings):
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


def create_endpoints(server, server_settings, ssl_settings):
	port = server_settings.Port
	interface = server_settings.Interface
	ssl_port = ssl_settings.SSLPort
	ssl_key = ssl_settings.SSLKeyPath
	ssl_cert = ssl_settings.SSLCertPath
	ssl_only = ssl_settings.SSLOnly
	if server_config.SSLSettings.SSLEnabled:
		print("SSLEnabled is True - Attempting to construct an SSL Endpoint...")
		if ssl_key is None or ssl_cert is None:
			print("Error constructing SSL Endpoint: Missing key/cert file.")
			if ssl_only:
				print("Error: SSLOnly is enabled and no SSL endpoint was created, so there is no endpoint. Terminating.")
				exit()
		else:
			ssl_endpoint = serverFromString(reactor, "ssl:{}:privateKey={}:certKey={}".format(ssl_port, ssl_key, ssl_cert))
			ssl_endpoint.listen(server)
			print("SSL Endpoint is now listening on port 6697.")
	if not ssl_only:
		print("Creating endpoint for port '{}', interface '{}'".format(port, interface))
		endpoint = serverFromString(reactor, "tcp:{}:interface={}".format(port, interface))
		endpoint.listen(server)
		print("Endpoint is now listening on port '{}'".format(port))


if __name__ == '__main__':
	if getuid() == 0:  # Prevent from running as root
		print("Error: You can not run this application as root.")

	ini_path = getcwd().strip("bin") + "/crow.ini"
	server_config = IRCConfig(ini_path)
	if not path.exists(ini_path):
		server_config.flush_config()
	config_output = server_config.read_config()

	if config_output is not None:  # config output is not yet implemented so this does nothing
		for output in config_output:
			print(output)

	server_instance = ChatServer(server_config)

	setup_loopingcalls(server_instance, server_config.ServerSettings, server_config.MaintenanceSettings)
	create_endpoints(server_instance, server_config.ServerSettings, server_config.SSLSettings)

	reactor.run()
