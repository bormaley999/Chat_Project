#  This Project has been made by Artem Manchenkov (artyom@manchenkoff.me) during the 3 day online course from Skillbox (https://skillbox.ru/)
#  Together with Artem I was able to solve the #TODO's section of the project.
#
#  Graphic wxPython 5 client for working with chat server
#
import wx
from twisted.internet import wxreactor

wxreactor.install()

from twisted.internet import reactor
from twisted.internet.protocol import ClientFactory
from twisted.protocols.basic import LineOnlyReceiver


class Client(LineOnlyReceiver):
    """Class for processing messages"""

    factory: 'Connector'

    def connectionMade(self):
        """Server connection setup handler"""

        self.factory.window.protocol = self  # recorded the current protocol in the application window

    def lineReceived(self, line):
        """Handler for receiving a new line from the server"""

        message = line.decode()  # раскодируем
        self.factory.window.text_box.AppendText(f"{message}\n")  # add to the message field


class Connector(ClientFactory):
    """Class for establishing a connection to the server"""

    window: 'ChatWindow'
    protocol = Client

    def __init__(self, app_window):
        """Remember the application window in the constructor for access"""

        self.window = app_window


class ChatWindow(wx.Frame):
    """Class for launching a graphical application"""

    protocol: Client  # протокол подключения
    text_box: wx.TextCtrl
    message_box: wx.TextCtrl
    submit_button: wx.Button

    def __init__(self):
        """Launching the application and handlers"""

        super().__init__(
            None,
            title='Chat window',
            size=wx.Size(350, 500)
        )

        self.build_widgets()

    def build_widgets(self):
        """Building the interface"""

        panel = wx.BoxSizer(wx.VERTICAL)

        # components
        self.text_box = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.message_box = wx.TextCtrl(self)
        self.message_box.SetHint("Your message")
        self.submit_button = wx.Button(self, label="Submit")

        # setup location
        panel.Add(self.text_box, flags=wx.SizerFlags(1).Expand())
        panel.Add(self.message_box, flags=wx.SizerFlags().Expand().Border(wx.ALL, 5))
        panel.Add(self.submit_button, flags=wx.SizerFlags().Expand().Border(wx.LEFT | wx.BOTTOM | wx.RIGHT, 5))

        # handlers
        self.submit_button.Bind(wx.EVT_BUTTON, self.send_message)

        # apply location to window
        self.SetSizer(panel)

    def send_message(self, event):
        """Message sending handler"""

        text_message = self.message_box.GetValue()

        self.protocol.sendLine(text_message.encode())  # has been sent
        self.message_box.SetValue('')  # has refreshed a text in field


if __name__ == '__main__':
    # created an app
    app = wx.App()

    # created a window
    window = ChatWindow()
    window.Show()

    # registered in the reactor
    # app.MainLoop()
    reactor.registerWxApp(app)

    # standard connection
    reactor.connectTCP(
        "localhost",
        7410,
        Connector(window)
    )

    reactor.run()
