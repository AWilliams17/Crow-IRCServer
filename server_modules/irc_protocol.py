from twisted.words.protocols.irc import IRC, IRCBadMessage, protocol, parsemsg
from server_modules.room import Room


class IRCProtocol(IRC):
    OUTPUT_DENOTE = "<= "

    def __init__(self, users, rooms):
        self.users = users
        self.rooms = rooms
        self.user_name = None
        self.state = "LoggedOut"

    def send_to_client(self, data):
        d = self.OUTPUT_DENOTE + data + "\n"
        self.transport.write(d.encode("utf-8"))

    def broadcast_msg(self, message, room):
        for user in room.users:
            irc_protocol = self.users[user][0]
            if irc_protocol != self:
                irc_protocol.sendLine(message)

    def connectionMade(self):
        self.send_to_client("Welcome to Rakuten Games chat server")
        self.send_to_client("Login name?")

    def connectionLost(self, reason=protocol.connectionDone):
        if self.user_name in self.users:
            room = self.get_room(self.user_name)
            if room:
                room.del_user(self.user_name)
            del self.users[self.user_name]

    def dataReceived(self, data):
        if data.rstrip() == "":
            return
        if self.state == "LoggedOut":
            self.handle_logged_out(data.rstrip())
        elif self.state == "LoggedIn":
            self.handle_logged_in(data.rstrip())
        elif self.state == "JoinedRoom":
            self.handle_joined_room(data.rstrip())
        else:
            self.send_to_client("In Unknown state : {}".format(self.state))

    def handle_command(self, data):
        prefix, command, params = parsemsg(data.decode('utf-8'))
        # mIRC is a big pile of doo-doo
        command = command.upper()
        print("prefix: %s command: %s params: %s" % (prefix, command, params))
        IRC.handleCommand(self, command, prefix, params)

    def handle_logged_out(self, name):
        if name[0] == '/':
            self.send_to_client("You can only use commands after login in. Please enter name to login.")
            return
        if name in self.users:
            self.send_to_client("Sorry, name taken.")
            return
        self.send_to_client("Welcome {}! Use /help to list all commands".format(name))
        self.user_name = name
        self.users[name] = [self, None]
        self.state = "LoggedIn"

    def handle_logged_in(self, command):
        self.handle_command(command)

    def handle_joined_room(self, message):
        if message[0] == '/':
            self.handle_command(message)
            return
        message = "{}: {}".format(self.user_name, message)
        current_room = self.get_room(self.user_name)
        self.broadcast_msg(message, current_room)

    def irc_unknown(self, prefix, command, params):
        self.send_to_client("Unknown command {}, please use /help to see available command.".format(command))

    def irc_rooms(self):
        if not self.rooms:
            self.send_to_client("No Active rooms. Use /join <room-name> to create new room.")
            return
        self.send_to_client("Active rooms are:")
        for room_name, room in self.rooms.iteritems():
            self.send_to_client("*" + room_name + " (" + str(len(room.users)) + ")")
        self.send_to_client("end of list.")

    def irc_JOIN(self, prefix, params):
        if not params:
            self.send_to_client("Please use : /join <room-name>")
        else:
            if self.users[self.user_name][1]:
                self.leave_current_room()
            self.send_to_client("entering room: {}".format(params[0]))
            self.join_room(params[0])
            self.state = "JoinedRoom"
            self.list_users(params[0])
            self.send_to_client(self.state)

    def irc_users(self, params):
        if not params:
            self.send_to_client("All Active users are:")
            for user in self.users:
                if user == self.user_name:
                    self.send_to_client("* {} (** this is you), Room : {}".format(
                        user, self.get_room(user).name if self.get_room(user) else None))
                else:
                    self.send_to_client(
                        "* {}, Room : {}".format(user, self.get_room(user).name if self.get_room(user) else None))
            self.send_to_client("end of list.")
        else:
            if params[0] not in self.rooms:
                self.send_to_client("Room {} not found.".format(params[0]))
            else:
                self.send_to_client("Active users in room {} are:".format(params[0]))
                self.list_users(params[0])

    def irc_leave(self):
        self.leave_current_room()
        self.state = "LoggedIn"

    def irc_quit(self):
        if self.get_room(self.user_name):
            self.leave_current_room()
        del self.users[self.user_name]
        self.transport.loseConnection()

    def irc_help(self):
        self.transport.write(
            "List of Commands: \n" +
            "   rooms - List active rooms \n" +
            "   users - List all active users or /users <room-name> to see users in a specific room \n" +
            "   join - Join a chat room  Ex: /join python \n" +
            "   leave - Leave the room you are currently in \n"
            "   msg - Send a private message.  Ex /msg thomas Hi there \n"
            "   help - Show this help \n"
            "   quit - Exit the program \n"
            )

    def irc_msg(self, params):
        current_room = self.get_room(self.user_name)
        if not current_room:
            self.send_to_client(
                "You can only send private message to a user in your room. "
                "Please join user's room to send them message.")
            return
        if not params:
            self.send_to_client("Usage /msg <user-name> message")
        else:
            if params[0] in self.users and params[0] not in current_room.users:
                self.send_to_client(
                    "User {} is not in current room, please join their room to send PM".format(params[0])
                )
            elif params[0] in current_room.users:
                irc_protocol = self.users[params[0]][0]
                irc_protocol.sendLine("PM from {} : {}".format(self.user_name, " ".join(params[1:])))
            else:
                self.send_to_client("User {} not found".format(params[0]))

    def list_users(self, room_name):
        for user in self.rooms[room_name].users:
            if user == self.user_name:
                self.send_to_client("* " + user.decode('utf-8') + " (** this is you)")
            else:
                self.send_to_client("* " + user.decode('utf-8'))
        self.send_to_client("end of list.")

    def join_room(self, room_name):
        if room_name in self.rooms:
            room = self.rooms[room_name]
        else:
            room = Room(room_name)
            self.rooms[room_name] = room
        self.users[self.user_name][1] = room
        room.add_user(self.user_name)
        self.join(self.user_name, room.name)
        self.broadcast_msg("* user has joined the room: {}".format(self.user_name), room)

    def leave_current_room(self):
        current_room = self.get_room(self.user_name)
        if current_room:
            self.send_to_client("leaving Room: {}".format(current_room.name))
            current_room.delUser(self.user_name)
            self.users[self.user_name][1] = None
            self.broadcast_msg("* user has left the room: {}".format(self.user_name), current_room)
        else:
            self.send_to_client("You're not in a room. Use /join <room-name> to join a room.")

    def get_room(self, user):
        return self.users[user][1]
