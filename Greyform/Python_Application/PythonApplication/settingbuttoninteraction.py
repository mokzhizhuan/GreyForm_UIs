class settingbuttonUI(object):
    def __init__(
        self,
        MarkingbackButton,
        stackedWidgetsetting,
        stackedWidget,
        HomeButton,
        WifiButton,
        serviceIPAddressButton,
        ServicesButton,
        UserButton,
        AboutButton,
        PowerButton,
        maintitlelabel,
    ):
        self.MarkingbackButton = MarkingbackButton
        self.stackedWidgetsetting = stackedWidgetsetting
        self.stackedWidget = stackedWidget
        self.HomeButton = HomeButton
        self.WifiButton = WifiButton
        self.serviceIPAddressButton = serviceIPAddressButton
        self.ServicesButton = ServicesButton
        self.UserButton = UserButton
        self.AboutButton = AboutButton
        self.PowerButton = PowerButton
        self.maintitlelabel = maintitlelabel
        self.button_UI()

    def button_UI(self):
        self.MarkingbackButton.clicked.connect(
            lambda: self.stackedWidgetsetting.setCurrentIndex(0)
        )
        self.MarkingbackButton.clicked.connect(self.homepages)
        self.MarkingbackButton.clicked.connect(
            lambda: self.stackedWidget.setCurrentIndex(4)
        )
        self.HomeButton.clicked.connect(self.homepages)
        self.HomeButton.clicked.connect(
            lambda: self.stackedWidgetsetting.setCurrentIndex(0)
        )
        self.WifiButton.clicked.connect(
            lambda: self.stackedWidgetsetting.setCurrentIndex(1)
        )
        self.WifiButton.clicked.connect(self.wifipages)
        self.serviceIPAddressButton.clicked.connect(
            lambda: self.stackedWidgetsetting.setCurrentIndex(2)
        )
        self.serviceIPAddressButton.clicked.connect(self.serviceIPAddresspages)
        self.ServicesButton.clicked.connect(
            lambda: self.stackedWidgetsetting.setCurrentIndex(3)
        )
        self.ServicesButton.clicked.connect(self.Servicespages)
        self.UserButton.clicked.connect(
            lambda: self.stackedWidgetsetting.setCurrentIndex(4)
        )
        self.UserButton.clicked.connect(self.Userpages)
        self.AboutButton.clicked.connect(
            lambda: self.stackedWidgetsetting.setCurrentIndex(5)
        )
        self.AboutButton.clicked.connect(self.Aboutpages)
        self.PowerButton.clicked.connect(
            lambda: self.stackedWidgetsetting.setCurrentIndex(6)
        )
        self.PowerButton.clicked.connect(self.Powerpages)

    # ui button setting
    def homepages(self):
        self.maintitlelabel.setText("<h3>Home Setting</h3>")

    def wifipages(self):
        self.maintitlelabel.setText("<h3>Wifi Setting</h3>")

    def serviceIPAddresspages(self):
        self.maintitlelabel.setText("<h3>Host Services</h3>")

    def Servicespages(self):
        self.maintitlelabel.setText("<h3>Services and Resolution Setting</h3>")

    def Userpages(self):
        self.maintitlelabel.setText("<h3>User Administration Localization Setting</h3>")

    def Aboutpages(self):
        self.maintitlelabel.setText("<h3>About Setting</h3>")

    def Powerpages(self):
        self.maintitlelabel.setText("<h3>Power Setting</h3>")
