from random import sample, choice
from string import ascii_lowercase, ascii_uppercase, digits


def generate_random_nick(protocol, in_use_nicknames, illegal_characters, max_length):
    """ For use in IRCUser - generate a random nick based off the protocol instance of the user.
    :param protocol: The protocol instance. Should be self.user.protocol
    :param in_use_nicknames: A list of nicknames that users are using to verify the generated nick isn't taken.
    :param illegal_characters: A set of illegal characters to use as a filter while generating the nickname.
    :param max_length: The server side max nickname length setting. The nickname will be cut off based on this value.
    """
    protocol_instance_string = str(protocol).replace(" ", "")
    random_nick = ''.join(sample(protocol_instance_string, len(protocol_instance_string)))
    random_nick_s = ''.join([c for c in random_nick[:max_length] if c not in illegal_characters])

    def validate_nick(nick, current_nicks):  # Check if the nick is still conflicting. Generate new one if yes.
        if nick in in_use_nicknames:
            def generate_junk(amount):
                return ''.join([
                    choice(
                        ascii_lowercase +
                        ascii_uppercase +
                        digits) for i in range(amount)
                ])

            # Re shuffle the string + Add random garbage to it and then re-validate it, keep it under nick length
            nick = (''.join(sample(nick, len(nick))) + generate_junk(15))[:max_length]
            validate_nick(nick, current_nicks)
        return nick

    random_nick_s = validate_nick(random_nick_s, in_use_nicknames)
    return random_nick_s
