from time import time
from copy import copy


class RateLimiter:
    """ Store a dict of hosts which also have a dict of commands with the last time they called the command. """
    def __init__(self):
        self.limited_hosts = {}

    def remove_old_limits(self):
        """ Clean up old entries in the dictionary. """
        limited_hosts_cached = copy(self.limited_hosts)
        current_time = int(time())
        for host in limited_hosts_cached:
            for command in limited_hosts_cached[host]:
                last_access_time = limited_hosts_cached[command]
                if current_time - last_access_time >= 120:
                    del self.limited_hosts[host][command]
            if len(limited_hosts_cached[host]) == 0:
                del self.limited_hosts[host]


def rate_limiter(command, duration=5, output_error=True):
    """
    A decorator which when applied to a command method that is called, will store the caller's
    host in the dictionary of currently limited hosts. Subsequent calls to the method will
    then compare the time of the current call to the previous call existing in the dictionary
    for the given command, and if it passes, then the command will be processed as normally.
    Otherwise, it will output a message if specified to.
    Args:
        command (str): The name of the command to map the method to. EG: if rate limiting nick, use NICK.
        duration (int): How long should the host have to wait before being able to make another call.
        output_error (bool): Whether or not to give the client the time remaining until he/she can make another call.
    """
    def command_decorator(command_method):
        def wrapper(*args):
            assert (duration <= 240)
            self = args[0]
            caller_host = self.user_instance.host
            limited_hosts = self.ratelimiter.limited_hosts

            current_time = int(time())
            limit_call = False
            time_remaining = 0

            if caller_host not in limited_hosts:
                limited_hosts[caller_host] = {}

            limited_commands = limited_hosts[caller_host]

            if command in limited_commands:
                last_access_time = limited_commands[command]
                elapsed_time = current_time - last_access_time
                if elapsed_time <= duration:
                    limit_call = True
                    time_remaining = duration - elapsed_time
                else:
                    del limited_commands[command]
            else:
                limited_commands[command] = current_time

            if limit_call:
                if output_error:
                    return self.sendLine(self.rplhelper.err_noprivileges(
                        "You are doing that too much. Please wait {} seconds and try again.".format(time_remaining)
                    ))
                return
            return command_method(*args)
        return wrapper
    return command_decorator
