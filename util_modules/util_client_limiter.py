class ClientLimiter:
    def __init__(self):
        """ For every host connected to the server, associate a value representing how many connections they have. """
        self.client_hosts = {}

    def add_entry(self, host):
        if host not in self.client_hosts:
            self.client_hosts[host] = 1
        else:
            self.client_hosts[host] += 1

    def remove_entry(self, host):
        if host in self.client_hosts:
            if self.client_hosts[host] == 1:
                del self.client_hosts[host]
            else:
                self.client_hosts[host] -= 1

    def host_has_too_many_clients(self, host, max_clients):
        if host in self.client_hosts and self.client_hosts[host] > max_clients:
            return True
        return False

