from time import time
from copy import copy
from random import choice
from string import ascii_uppercase, ascii_lowercase, digits


class PingManager:
    def __init__(self, users):
        self.users = users
        self.ping_queue = {}

    def ping_users(self):
        ping_msg = ''.join([choice(ascii_lowercase + ascii_uppercase + digits) for i in range(15)])
        print(ping_msg)
        if len(self.ping_queue) != 0:  # Some people have failed to respond since the last ping. Disconnect them.
            queue_copy = copy(self.ping_queue)
            for user in queue_copy:
                if user in self.users:  # Make sure they didn't disconnect and weren't removed from the queue(somehow)
                    user_last_ping = self.ping_queue[user][1]
                    time_elapsed = user_last_ping - int(time())
                    user.irc_QUIT([], [], time_elapsed)
                del self.ping_queue[user]  # Not going to bother creating more overhead by calling remove from queue
        for user in self.users:  # Anyway, ping everyone who is still here.
            ping_time = int(time())
            self.ping_queue[user] = [user, ping_time, ping_msg]
            user.sendLine("PING :{}".format(ping_msg))

    def pong_received(self, user, ping_message):
        if user in self.ping_queue:  # Ignore someone who is sending a PONG response manually.
            if len(ping_message) == 0 or self.ping_queue[user][2] != ping_message[0]:  # Validate response
                user_last_ping = self.ping_queue[user][1]
                time_elapsed = user_last_ping - int(time())
                user.irc_QUIT([], [], time_elapsed)
            del self.ping_queue[user]

    def remove_from_queue(self, user):
        """ Called by a client when it disconnects. """
        if user in self.ping_queue:
            del self.ping_queue[user]
