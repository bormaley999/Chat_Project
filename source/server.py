#  This Project has been made by Artem Manchenkov (artyom@manchenkoff.me) during the 3 day online course from Skillbox (https://skillbox.ru/)
#  Together with Artem I was able to solve the #TODO's section of the project.
#
#  Server for processing messages from clients
#
from twisted.internet import reactor
from twisted.protocols.basic import LineOnlyReceiver
from twisted.internet.protocol import ServerFactory, connectionDone


class Client(LineOnlyReceiver):
    """Class for processing connection with server client"""

    delimiter = "\r\n".encode()  # \n for terminal, \r\n for GUI

    # specifying a factory for processing connections
    factory: 'Server'

    # info about a client
    ip: str
    login: str = None

    def connectionMade(self):
        """New Client Handler
        - record IP
        - add to customer list
        - send a greeting message
        """

        self.ip = self.transport.getPeer().host  # write client IP address
        self.factory.clients.append(self)  # add to factory customer list

        self.sendLine("Welcome to the chat!".encode())  # send a message to the client

        print(f"Client {self.ip} connected")  # display a message in the server console

    def connectionLost(self, reason=connectionDone):
        """Connection Closure Handler
        - remove from the list of clients
        - display a chat message about disconnection
        """

        self.factory.clients.remove(self)  # remove the client from the list in the factory

        print(f"Client {self.ip} disconnected")  # display a notification in the server console

    def lineReceived(self, line: bytes):
        """Handler for a new message from a client
        - register, if this is the first entry, notify chat
        - forward the message to the chat, if already registered
        """

        message = line.decode()  # decode the received message into a string

        # if login is not registered yet
        if self.login is None:
            if message.startswith("login:"):  # we check that login is at the beginning:
                user_login = message.replace("login:", "")  # cut the part after:

                # TODO: login existence check
                for user in self.factory.clients:
                    if user_login == user.login:
                        error = f"Login {user_login} already exists!"
                        self.sendLine(error.encode())
                        self.transport.loseConnection()
                        return

                self.login = user_login

                notification = f"New user: {self.login}"  # we generate a notification about a new client
                self.factory.notify_all_users(notification)  # send everyone to chat

                # TODO: send 10 messages to a new client
                self.send_history()
            else:
                self.sendLine("Invalid login".encode())  # sends a notification if there is an error in the message
                # if you already have a login and this is the next message

        else:
            format_message = f"{self.login}: {message}"  # format the message on behalf of the client

            # TODO: save messages to list
            self.factory.messages.append(format_message)

            # send to everyone in the chat and in the server console
            self.factory.notify_all_users(format_message)
            print(format_message)

    def send_history(self):
        # sending last 10 messages
        pass


class Server(ServerFactory):
    """Class for server management"""

    clients: list  # list of clients
    messages: list
    protocol = Client  # client processing protocol

    def __init__(self):
        """Server start
        - initialization of the client list
        - display notification in the console
        """

        self.clients = []  # create an empty customer list
        self.messages = []

        print("Server started - OK")  # notification to the server console

    def startFactory(self):
        """Starting client listening (notification to the console)"""

        print("Start listening ...")  # notification to the server console

    def notify_all_users(self, message: str):
        """
        Sending a message to all chat clients :param message: Message text
        """

        data = message.encode()  # encode the text in binary representation

        # send to all connected clients
        for user in self.clients:
            user.sendLine(data)


if __name__ == '__main__':
    # listening options
    reactor.listenTCP(
        7410,
        Server()
    )

    # start the reactor
    reactor.run()
