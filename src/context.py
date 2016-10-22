Features = {"CASEMAPPING": "rfc1459", "CHARSET": "utf-8", "STATUSMSG": "@+"} # IRC server features (these are defaults)

class IRCContext:
    """Base class for channels and users."""

    is_channel = False
    is_user = False
    is_fake = False

    def __init__(self, name, client):
        self.name = name
        self.client = client

    def get_send_type(self, *, is_notice=False, is_privmsg=False):
        if is_notice and not is_privmsg:
            return "NOTICE"
        return "PRIVMSG"

    @staticmethod
    def raw_send(data, client, send_type, name):
        full_address = "{cli.nickname}!{cli.ident}@{cli.hostmask}".format(cli=client)

        # Maximum length of sent data is 0x200 (512) bytes. However,
        # we have to reduce the maximum length allowed to account for:
        # 1 (1) - The initial colon at the front of the data
        # 2 (1) - The space between the command and the target
        # 2 (1) - The space between the target and the data
        # 3 (1) - The colon at the front of the data to send
        length = 0x200 - 4
        # Next, we need to reduce the length to account for our address
        length -= len(full_address)
        # Then we also need to account for the target's length
        length -= len(name)
        # Finally, we need to account for the send type's length
        length -= len(send_type)

        for line in data.splitlines():
            while line:
                extra, line = line[:length], line[length:]
                client.send("{0} {1} :{2}".format(send_type, name, extra))

    def send(self, data, target=None, *, notice=False, privmsg=False):
        send_type = self.get_send_type(is_notice=notice, is_privmsg=privmsg)
        self.raw_send(data, self.client, send_type, self.name)