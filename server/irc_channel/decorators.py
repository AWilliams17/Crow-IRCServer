def user_in_channel(method):
    def wrapper(self, *args):
        caller_protocol = args[0]
        caller_user = caller_protocol.user_instance
        if caller_user in self.users:
            return method(self, args)
        return caller_protocol.sendLine(caller_user.rplhelper.err_notonchannel("You must be in the channel to use that command."))
    return wrapper

