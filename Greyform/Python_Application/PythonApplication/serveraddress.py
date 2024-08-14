from PyQt5.QtNetwork import QTcpServer, QHostAddress


# port localhost default
class MyServer(QTcpServer):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.peer_address = QHostAddress.LocalHost  # Initialize peer address
        self.peer_port = 8080  # Initialize peer port
        self.listen(QHostAddress.LocalHost, 8080)
