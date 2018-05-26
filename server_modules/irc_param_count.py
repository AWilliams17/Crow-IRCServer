def min_param_count(count, additional_information=None):
    """
    Decorator - Ensures that the decorated irc command method meets the minimum argument count.
    Args:
        count: The minimum amount of arguments the command requires.
        additional_information: If specified, this is appended in a new line after the error message.
    The irc command methods all follow the same prefix, irc_, and they all take the same three parameters:
    self, prefix, and params, where params is the list of arguments passed to the command by the client.
    """
    def command_decorator(command_method):
        def wrapper(*args):
            assert command_method.__name__.startswith('irc_')
            command_name = command_method.__name__[4:]  # irc command methods are prefixed with irc_.
            self = args[0]
            if len(args[2]) >= count:
                return command_method(*args)
            error_message = self.rplhelper.err_needmoreparams(command_name)
            if additional_information is not None:
                error_message += "\r\n{}".format(additional_information)
            return self.sendLine(error_message)
        return wrapper
    return command_decorator
