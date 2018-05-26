from time import time


class ChannelManager:
    """ Used to delete old channels on the server, and prevent the creation of further channels for a given host. Also,
    warn channels that are approaching their expiration date."""
    def __init__(self, channels, channel_ultimatum):
        self.channels = channels
        self.ultimatum = channel_ultimatum

    def channel_maintenance(self):
        for _channel in self.channels:
            channel = self.channels[_channel]
            current_time = int(time())
            time_elapsed = int((current_time - channel.last_owner_login) / 86400)  # how many days since the last login
            time_remaining = self.ultimatum - time_elapsed
            if channel.channel_owner is None:
                if channel.scheduled_for_deletion:
                    print("Goodbye channel")
                else:
                    if time_remaining <= 0:
                        channel.broadcast_notice("ALERT - Channel is now scheduled for deletion!")
                        channel.broadcast_notice("Deletion will be cancelled if owner logs in before next sweep.")
                        channel.scheduled_for_deletion = True
                    elif time_remaining < 3:
                        channel.broadcast_notice("ALERT - Channel will be scheduled for deletion in {}"
                                                 " days if owner does not login.".format(time_remaining))
