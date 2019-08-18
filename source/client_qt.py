#  This Project has been made by Artem Manchenkov (artyom@manchenkoff.me) during the 3 day online course from Skillbox (https://skillbox.ru/)
#  Together with Artem I was able to solve the #TODO's section of the project.
#
#  Graphic PyQt 5 client for working with chat server
#
import sys
from PyQt5 import QtWidgets
from gui import design

from twisted.internet.protocol import ClientFactory
from twisted.protocols.basic import LineOnlyReceiver


class Client(LineOnlyReceiver):
    """Class for processing messages"""

    factory: 'Connector'

    def connectionMade(self):
        """Server connection setup handler"""

        self.factory.window.protocol = self  # recorded the current protocol in the application window

    def lineReceived(self, line: bytes):
        """Handler for receiving a new line from the server"""

        message = line.decode()  # decode
        self.factory.window.plainTextEdit.appendPlainText(message)  # add to the message field


class Connector(ClientFactory):
    """Class for establishing a connection to the server"""

    window: 'ChatWindow'
    protocol = Client

    def __init__(self, app_window):
        """Remember the application window in the constructor for access"""

        self.window = app_window


class ChatWindow(QtWidgets.QMainWindow, design.Ui_MainWindow):
    """Class for launching a graphical application"""

    protocol: Client  # connection protocol
    reactor = None  # reference to the rector for appeal

    def __init__(self):
        """Launching the application and handlers"""

        super().__init__()
        self.setupUi(self)  # load interface
        self.init_handlers()  # configure action handlers

    def init_handlers(self):
        """Creating action handlers (buttons, fields, etc.)"""

        self.pushButton.clicked.connect(self.send_message)  # button click event

    def closeEvent(self, event):
        """Window close handler"""

        self.reactor.callFromThread(self.reactor.stop)  # reactor shutdown

    def send_message(self):
        """Handler for sending messages to the server"""

        message = self.lineEdit.text()

        self.protocol.sendLine(message.encode())  # sent to the server
        self.lineEdit.setText('')  # text reset


if __name__ == '__main__':
    # create an app
    app = QtWidgets.QApplication(sys.argv)

    # export a reactor for Qt
    import qt5reactor

    # create a UI window
    window = ChatWindow()
    window.show()

    # Qt reactor setup
    qt5reactor.install()

    # import a standard reactor
    from twisted.internet import reactor

    # standard reactor start
    reactor.connectTCP(
        "localhost",
        7410,
        Connector(window)
    )

    # transfer it also to the contact window
    window.reactor = reactor
    reactor.run()
