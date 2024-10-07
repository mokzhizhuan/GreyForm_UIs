from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import psutil
import os
import datetime

#text implementation for setting
class SettingText(object):
    def __init__(
        self,
        labeltitlsetting,
        titlelabel,
        info_label,
        version_label,
        author_label,
        SystemDate,
        SystemMemory,
        PasslineEdit,
        userlabel,
        accountinfo,
    ):
        self.labeltitlsetting = labeltitlsetting
        self.titlelabel = titlelabel
        self.info_label = info_label
        self.version_label = version_label
        self.author_label = author_label
        self.SystemDate = SystemDate
        self.SystemMemory = SystemMemory
        self.PasslineEdit = PasslineEdit
        self.userlabel = userlabel
        self.accountinfo = accountinfo
        self.retranslateUi()


    # add text
    def retranslateUi(self):
        self.labeltitlsetting.setText("<h3>Setting</h3>")
        self.titlelabel.setText("<h3>About My Application</h3>")
        self.info_label.setText("This is a Robot Marking Application program")
        self.version_label.setText("Version: 1.0")
        self.author_label.setText("Created by Mok Zhi Zhuan")
        datetoday = datetime.date.today()
        datetodayformatted = datetoday.strftime("%d/%m/%Y")
        process = psutil.Process(os.getpid())
        memory_usage = process.memory_info().rss / (1024 * 1024)  # in MB
        self.SystemDate.setText(f"Date : {datetodayformatted}")
        self.SystemMemory.setText(f"System Memory Usage : {memory_usage:.2f} MB")
        self.userlabel.setText(f"<h2>User: {self.accountinfo[0]['UserID']}</h2>")
        self.PasslineEdit.setText(f"{self.accountinfo[0]['Pass']}")
        self.PasslineEdit.returnPressed.connect(self.changepassfunction)

    #change pass ui loader
    def changepassfunction(self):
        password = self.PasslineEdit.text()
        self.accountinfo[0]["Pass"] = password
