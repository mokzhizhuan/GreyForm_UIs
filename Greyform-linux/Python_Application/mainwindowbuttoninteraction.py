import PythonApplication.menu_close as closewindow
import PythonApplication.menuconfirm as backtomenudialog
import PythonApplication.fileselectionmesh as fileselectionmesh
import PythonApplication.menu_confirmack as confirmack
import PythonApplication.setting as setting
import PythonApplication.enable_robot as robotenabler


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
        EnableRobotButton,
        SettingButton,
        append_filter,
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
        self.EnableRobotButton = EnableRobotButton
        self.SettingButton = SettingButton
        self.append_filter = append_filter
        self.button_UI()

    def button_UI(self):
        self.menuStartButton.clicked.connect(
            lambda: self.stackedWidget.setCurrentIndex(1)
        )
        self.menuCloseButton.clicked.connect(
            lambda: closewindow.Ui_Dialog_Close.show_dialog_close(self.mainwindow)
        )
        self.NextButton_Page_2.clicked.connect(
            lambda: self.mainwindow.stackedWidget.setCurrentIndex(2)
        )
        self.BacktoMenuButton.clicked.connect(
            lambda: backtomenudialog.Ui_Dialog_Confirm.show_dialog_confirm(
                self.mainwindow, self.stackedWidget
            )
        )
        self.BackButton_Page_2.clicked.connect(
            lambda: self.stackedWidget.setCurrentIndex(1)
        )
        self.BackButton_Page_3.clicked.connect(
            lambda: self.stackedWidget.setCurrentIndex(2)
        )
        self.NextButton_Page_3.clicked.connect(
            lambda: self.stackedWidget.setCurrentIndex(3)
        )
        self.ConfirmButton.clicked.connect(
            lambda: self.stackedWidget.setCurrentIndex(4)
        )
        self.HomeButton.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))
        self.CloseButton.clicked.connect(
            lambda: closewindow.Ui_Dialog_Close.show_dialog_close(self.mainwindow)
        )
        self.ConfirmAckButton.clicked.connect(
            lambda: confirmack.Ui_Dialog_ConfirmAck.show_dialog_ConfirmAck(
                self.mainwindow, self.append_filter
            )
        )
        self.MarkingButton.clicked.connect(
            lambda: self.stackedWidget.setCurrentIndex(3)
        )
        self.SettingButton.clicked.connect(
            lambda: self.stackedWidget.setCurrentIndex(5)
        )

