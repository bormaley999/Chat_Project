#  This Project has been made by Artem Manchenkov (artyom@manchenkoff.me) during the 3 day online course from Skillbox(https://skillbox.ru/)
#  Together with Artem I was able to solve the #TODO's section of the project.
#  Console client to connect to a server
#

from twisted.internet import reactor, stdio
from twisted.internet.protocol import Protocol, ClientFactory


class MessageHandler(Protocol):
    """Class for parallel Input /Output"""

    output = None  # path to display messages from the console

    def dataReceived(self, data: bytes):
        """Handler for a new message from the server / user input"""

        if self.output:
            self.output.write(data)  # redirect the message to the server


class User(MessageHandler):
    """Class for sending / processing server messages"""

    factory: 'Connector'

    def wrap(self):
        """Terminal Input /Output Processing"""

        handler = MessageHandler()  # create an intermediate object for working with input / output in the console
        handler.output = self.transport  # assign a path for outputting messages (to the server)

        wrapper = stdio.StandardIO(handler)  # run the Twisted module for parallel input and data acquisition

        self.output = wrapper  # substitute into the current protocol (it will intercept by pressing Enter)

    def connectionMade(self):
        """
        Successful Connection Handler
        - send login to server
        - run input / output
        """

        login_message = f"login:{self.factory.login}"  # form a login registration line
        self.send_message(login_message)  # send to a server

        self.wrap()  # enable the input / output mode in the console (to send messages by pressing Enter)

    def send_message(self, content: str):
        """Handler for sending messages to the server"""

        data = f"{content}\n".encode()  # encode the text in binary representation
        self.transport.write(data)  # send to a server


class Connector(ClientFactory):
    """Class for creating a server connection"""

    protocol = User
    login: str

    def __init__(self, login: str):
        """Creating a connection manager (save username)"""

        self.login = login  # write down the login for subsequent registration

    def startedConnecting(self, connector):
        """Connection setup handler (display a message)"""

        print("Connecting to the server...")  # client console notification

    def clientConnectionFailed(self, connector, reason):
        """Handler of a failed connection (turn off the reactor)"""

        print("Connection failed")  # client console notification
        reactor.callFromThread(reactor.stop)  # reactor shutdown

    def clientConnectionLost(self, connector, reason):
        """Connection disconnection handler (disable reactor)"""

        print("Disconnected from the server")  # client console notification
        reactor.callFromThread(reactor.stop)  # reactor shutdown


if __name__ == '__main__':
    # request username for connection
    user_login = input("Your login: ")

    # connection parameters
    reactor.connectTCP(
        "localhost",
        7410,
        Connector(user_login)
    )

    # start a reactor
    reactor.run()
