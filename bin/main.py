from server_modules.irc_server import ChatServer
from twisted.internet import reactor

if __name__ == '__main__':
	reactor.listenTCP(6667, ChatServer())
	reactor.run()
