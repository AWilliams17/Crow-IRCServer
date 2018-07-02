from secrets import token_urlsafe


def get_operator(self, caller, name=None):
    """  If name is none, list all operator names in channel. otherwise, attempt to list all details which pertain
    to an operator with the given name. """
    if self.op_accounts:
        if name is None:
            return "Get Account: (Channel: {} - listing all account names: {})".format(self.channel_name, str([i for i in self.op_accounts.keys()]))
        account_details = next((x for x in self.op_accounts if x == name), None)
        if account_details is not None:
            return "Get Account: (Channel: {} - Username: {} - results: {})".format(self.channel_name, name, self.op_accounts.get(name))
        return "Get Account: (Channel: {} - Username: {} - An account with that name does not exist.)".format(self.channel_name, name)
    return "Get Account: (Channel: {} - There are no operator accounts for this channel.)".format(self.channel_name)


def add_operator(self, caller, name):
    """ Add a new operator account using the given name. """
    if name in self.op_accounts:
        return "Add Account: (Channel: {} - Username: {} - That name is already in use.)".format(self.channel_name, name)
    elif name is None:
        return "Add Account: (Channel: {} - Username: None - Name cannot be None.)".format(self.channel_name)
    account_password = token_urlsafe(32)
    self.op_accounts[name] = {
        "current_user": None,
        "password": account_password,
        "permissions": []
    }
    return "Add Account: (Channel: {} - Username: {} - Password: {} - Account added.)".format(self.channel_name, name, account_password)


def delete_operator(self, caller, name):
    """ Delete an operator account using the given name. """
    if name not in self.op_accounts:
        return "Delete Account: (Channel: {} - Username: {} - Account with that name does not exist.)".format(self.channel_name, name)
    elif name is None:
        return "Delete Account: (Channel: {} - Username: None - Name cannot be None.)".format(self.channel_name)
    logged_user = self.op_accounts[name]["current_user"]
    if logged_user is not None:
        logged_user.protocol.send_msg(logged_user.nickname, "{}: The account you were logged into has been deleted.".format(self.channel_name))
    del self.op_accounts[name]
    return "Delete Account: (Channel: {} - Username: {} - Account was Deleted.)".format(self.channel_name, name)


def set_operator_name(self, caller, name, new_name):
    """ Set an existing operator account's name to the specified new one. """
    if name not in self.op_accounts:
        return "Set Account Name: (Channel: {} - Username: {} - Account with that name does not exist.)".format(self.channel_name, name)
    elif name is None or new_name is None:
        return "Set Account Name: (Channel: {} - You must supply all parameters (name, new usernamename)".format(self.channel_name)
    logged_user = self.op_accounts[name]["current_user"]
    if logged_user is not None:
        logged_user.protocol.send_msg(logged_user.nickname, "{}: The name of the account you were logged into has been changed to '{}'".format(self.channel_name, new_name))
    self.op_accounts[new_name] = self.op_accounts.pop(name)
    return "Set Account Name: (Channel: {} - Username: {} - Account name changed.)".format(self.channel_name, name)


def set_operator_password(self, caller, name, new_password):
    """ Set an existing operator account's password to the specified new one. """
    if name not in self.op_accounts:
        return "Set Account Password: (Channel: {} - Username: {} - Account with that name does not exist.)".format(self.channel_name, name)
    elif name is None or new_password is None:
        return "Set Account Name: (Channel: {} - You must supply all parameters (usernamename, new password)".format(self.channel_name)
    logged_user = self.op_accounts[name]["current_user"]
    if logged_user is not None:
        logged_user.protocol.send_msg(logged_user.nickname, "{}: The name of the account you were logged into has been changed to '{}'".format(self.channel_name, new_password))
    self.op_accounts[name]["password"] = new_password
    return "Set Account Password: (Channel: {} - Username: {} - Account Password changed.)".format(self.channel_name, name)
