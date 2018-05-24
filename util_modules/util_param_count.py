def min_param_count(count, additional_information=None):
    """ A decorator which enforces irc command argument counts. For use inside the IRCProtocol class.
    :param count: How many arguments does the command need.
    """
    def command_decorator(command_method):
        def wrapper(*args):
            assert (command_method.__name__.startswith('irc_'))
            command_name = command_method.__name__[4:]  # irc command methods are prefixed with irc_.
            self = args[0]
            if len(args[2]) >= count:
                return command_method(*args)
            error_message = self.rplhelper.err_needmoreparams(command_name)
            if additional_information is not None:
                error_message += "\r\n%s", additional_information
            return self.sendLine(error_message)
        return wrapper
    return command_decorator
