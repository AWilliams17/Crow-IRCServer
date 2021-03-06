def authorization_required(requires_operator=False, requires_channel_owner=False):
    if requires_operator and requires_channel_owner:
        requires_operator = False  # A channel owner wouldn't have an operator account, so it would fail any checks.

    def authorization_decorator(method):
        # ToDo: Documentation
        def wrapper(self, *args):
            caller_user = args[0]
            if caller_user in self.users:
                if (requires_operator and caller_user in self.op_accounts) or (requires_channel_owner and caller_user is self.channel_owner):
                    return method(self, *args)
                return caller_user.rplhelper.err_noprivileges("You lack authorization to use that command.")
            return caller_user.rplhelper.err_notonchannel("You must be in the channel to invoke that command.")
        return wrapper
    return authorization_decorator

