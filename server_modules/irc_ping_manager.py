from time import time
from copy import copy


class PingManager:
    def __init__(self, users):
        self.users = users
        self.ping_queue = {}

    def ping_users(self):
        print("Ping method called.")
        if len(self.ping_queue) != 0:  # Some people have failed to respond since the last ping. Disconnect them.
            queue_copy = copy(self.ping_queue)
            for user in queue_copy:
                if user in self.users:  # Make sure they didn't disconnect and weren't removed from the queue.
                    user_last_ping = self.ping_queue[user][1]
                    time_elapsed = user_last_ping - int(time())
                    user.irc_QUIT([], [], time_elapsed)
                del self.ping_queue[user]
        for user in self.users:  # Anyway, ping everyone who is still here.
            print("Pinging someone")
            ping_time = int(time())
            self.ping_queue[user] = [user, ping_time, 1]
            user.sendLine("PING :{}".format(user.hostname))

    def pong_received(self, user):
        pong_time = int(time())
        print("Pong was received: {}".format(pong_time))
        if user in self.ping_queue:  # Ignore someone who is sending a PONG response manually.
            user_last_ping = self.ping_queue[user][1]
            total_pings = self.ping_queue[user][2]
            reply_time = pong_time - user_last_ping
            if reply_time >= 5:  # Took them a little while to respond.
                if total_pings < 3:  # If they've had less than 3 attempts for a sane reply time, ping em again.
                    ping_time = int(time())
                    total_pings += 1
                    self.ping_queue[user] = [user, ping_time, total_pings]
                    user.sendLine("PING :{}".format(user.hostname))
                else:  # otherwise, they're too laggy. get rid of them.
                    user.irc_QUIT([], [], reply_time)
                    del self.ping_queue[user]
            else:  # Reply time satisfactory. Remove them from the queue.
                del self.ping_queue[user]
