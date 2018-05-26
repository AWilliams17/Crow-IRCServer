from time import time


class ChannelManager:
    """ Used to delete old channels on the server, and prevent the creation of further channels for a given host. Also,
    warn channels that are approaching their expiration date."""
    def __init__(self, channels, channel_ultimatum):
        self.channels = channels
        self.ultimatum = channel_ultimatum

    def channel_maintenance(self):
        for channel in self.channels:
            current_time = int(time())
            time_elapsed = (current_time - channel.last_owner_login) / 3600  # how many days since the last login
            time_remaining = self.ultimatum - time_elapsed
            if channel.scheduled_for_deletion:
                print("Goodbye channel")
            else:
                if time_remaining < 3:
                    print("Channel is going to soon be deleted")
                    pass  # ToDo: Tell everyone their channel is about to be deleted.
                if time_remaining <= 0:
                    print("Channel will be deleted")
                    channel.scheduled_for_deletion = True
                    pass  # ToDo: Tell everyone their channel is scheduled for deletion.
