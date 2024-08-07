import PythonApplication.menu_close as closewindow
import PythonApplication.menuconfirm as backtomenudialog
import PythonApplication.menu_confirmack as confirmack


class mainwindowbuttonUI(object):
    def __init__(
        self,
        mainwindow,
        stackedWidget,
        menuStartButton,
        menuCloseButton,
        NextButton_Page_2,
        BacktoMenuButton,
        BackButton_Page_2,
        BackButton_Page_3,
        NextButton_Page_3,
        ConfirmButton,
        HomeButton,
        CloseButton,
        ConfirmAckButton,
        MarkingButton,
    ):
        self.mainwindow = mainwindow
        self.stackedWidget = stackedWidget
        self.menuStartButton = menuStartButton
        self.menuCloseButton = menuCloseButton
        self.NextButton_Page_2 = NextButton_Page_2
        self.BacktoMenuButton = BacktoMenuButton
        self.BackButton_Page_2 = BackButton_Page_2
        self.BackButton_Page_3 = BackButton_Page_3
        self.NextButton_Page_3 = NextButton_Page_3
        self.ConfirmButton = ConfirmButton
        self.HomeButton = HomeButton
        self.CloseButton = CloseButton
        self.ConfirmAckButton = ConfirmAckButton
        self.MarkingButton = MarkingButton
        self.button_UI()

    def startconfigure(self):
        self.stackedWidget.setCurrentIndex(1)

    def configurestage(self):
        self.stackedWidget.setCurrentIndex(2)

    def guiconfigure(self):
        self.stackedWidget.setCurrentIndex(3)

    def guibuttonconfig(self):
        self.stackedWidget.setCurrentIndex(4)

    def homeui(self):
        self.stackedWidget.setCurrentIndex(0)

    def button_UI(self):
        self.menuStartButton.clicked.connect(self.startconfigure)
        self.menuCloseButton.clicked.connect(
            lambda: closewindow.Ui_Dialog_Close.show_dialog_close(self.mainwindow)
        )
        self.NextButton_Page_2.clicked.connect(self.configurestage)
        self.BacktoMenuButton.clicked.connect(
            lambda: backtomenudialog.Ui_Dialog_Confirm.show_dialog_confirm(
                self.mainwindow,
                self.stackedWidget,
            )
        )
        self.BackButton_Page_2.clicked.connect(self.startconfigure)
        self.BackButton_Page_3.clicked.connect(self.configurestage)
        self.NextButton_Page_3.clicked.connect(self.guiconfigure)
        self.ConfirmButton.clicked.connect(self.guibuttonconfig)
        self.MarkingButton.clicked.connect(self.guiconfigure)
        self.HomeButton.clicked.connect(self.homeui)
        self.CloseButton.clicked.connect(
            lambda: closewindow.Ui_Dialog_Close.show_dialog_close(self.mainwindow)
        )
        self.ConfirmAckButton.clicked.connect(
            lambda: confirmack.Ui_Dialog_ConfirmAck.show_dialog_ConfirmAck(
                self.mainwindow
            )
        )
