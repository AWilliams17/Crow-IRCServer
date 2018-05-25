from server_modules.irc_server import ChatServer
from server_modules.irc_config import IRCConfig
from twisted.internet import reactor, task


def load_config():
	config = IRCConfig()
	if not config.config_exists():
		print("Configuration file does not exist, creating one...")
		creation_errors = config.create_config()
		if creation_errors is not None:
			print("Failed to create config: {}".format(creation_errors))
			exit()
		print("Done.")
		print(
			"\nNote: The default settings have the port set to 6667 and the interface set to 127.0.0.1, "
			"meaning the server will be run on localhost. \nIf you wish to change this, the config name is crow.ini,"
			"located in {}.\nThere also are two default operator accounts with very insecure usernames and passwords.\n"
			"Refer to INI_DOCS.TXT on the repo for setting up the ini"
			"if you don't know what a certain setting does.\n".format(config.config_path())
		)

	read_errors = config.read_config()
	if read_errors is not None:
		print("Failed to read config: {}".format(read_errors))
		exit()

	return config


def setup_maintenance_methods(server_instance, maintenance_settings):
	ratelimitclearinterval = maintenance_settings["RateLimitClearInterval"]
	flushinterval = maintenance_settings["FlushInterval"]
	channelscaninterval = maintenance_settings["ChannelScanInterval"]

	if ratelimitclearinterval != 0:
		task.LoopingCall(server_instance.maintenance_ratelimiter).start(ratelimitclearinterval)

	if flushinterval != 0:
		task.LoopingCall(server_instance.maintenance_flush_server).start(flushinterval)

	if channelscaninterval != 0:
		task.LoopingCall(server_instance.maintenance_delete_old_channels).start(channelscaninterval)


if __name__ == '__main__':
	server_config = load_config()
	server_port = server_config.ServerSettings['Port']
	server_interface = server_config.ServerSettings['Interface']
	server_instance = ChatServer(server_config)
	setup_maintenance_methods(server_instance, server_config.MaintenanceSettings)

	reactor.listenTCP(server_port, server_instance, interface=server_interface)
	reactor.run()
