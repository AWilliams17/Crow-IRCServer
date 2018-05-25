from server_modules.irc_server import ChatServer
from server_modules.irc_config import IRCConfig
from twisted.internet import reactor

if __name__ == '__main__':
	config = IRCConfig()
	if not config.config_exists():
		print("Configuration file does not exist, creating one...")
		creation_errors = config.create_config()
		if creation_errors is not None:
			print("Failed to create config: {}".format(creation_errors))
			exit()
		print("Done.")

	read_errors = config.read_config()
	if read_errors is not None:
		print("Failed to read config: {}".format(read_errors))
		exit()

	reactor.listenTCP(config.ServerSettings['Port'], ChatServer(config))
	reactor.run()
