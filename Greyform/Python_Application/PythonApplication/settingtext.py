from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from pywifi import PyWiFi, const
import PythonApplication.serveraddress as server
import psutil
import os
import datetime
import socket


class SettingText(object):
    def __init__(
        self,
        labeltitlsetting,
        ip_label,
        titlelabel,
        info_label,
        version_label,
        author_label,
        Portnumipadd,
        host,
        Port,
        SystemDate,
        SystemMemory,
        PasslineEdit,
        userlabel,
        accountinfo,
    ):
        self.labeltitlsetting = labeltitlsetting
        self.ip_label = ip_label
        self.titlelabel = titlelabel
        self.info_label = info_label
        self.version_label = version_label
        self.author_label = author_label
        self.Portnumipadd = Portnumipadd
        self.host = host
        self.Port = Port
        self.SystemDate = SystemDate
        self.SystemMemory = SystemMemory
        self.PasslineEdit = PasslineEdit
        self.userlabel = userlabel
        self.accountinfo = accountinfo
        self.retranslateUi()

    # detect ip address
    def get_ip_address(self):
        # Get the IP address of the local machine
        ip_address = socket.gethostbyname(socket.gethostname())
        return ip_address

    # add text
    def retranslateUi(self):
        ip_address = self.get_ip_address()
        self.labeltitlsetting.setText("<h3>Setting</h3>")
        self.ip_label.setText(f"IP Address: {ip_address}")
        self.titlelabel.setText("<h3>About My Application</h3>")
        self.info_label.setText("This is a Robot Marking Application program")
        self.version_label.setText("Version: 1.0")
        self.author_label.setText("Created by Mok Zhi Zhuan")
        servers = server.MyServer()
        self.Portnumipadd.setText(f"Port: {servers.serverPort()}")
        self.host.setText(f"Host: {servers.serverAddress().toString()}")
        self.Port.setText(f"Port: {servers.serverPort()}")
        datetoday = datetime.date.today()
        datetodayformatted = datetoday.strftime("%d/%m/%Y")
        process = psutil.Process(os.getpid())
        memory_usage = process.memory_info().rss / (1024 * 1024)  # in MB
        self.SystemDate.setText(f"Date : {datetodayformatted}")
        self.SystemMemory.setText(f"System Memory Usage : {memory_usage:.2f} MB")
        self.userlabel.setText(f"<h2>User: {self.accountinfo[0]['UserID']}</h2>")
        self.PasslineEdit.setText(f"{self.accountinfo[0]['Pass']}")
        self.PasslineEdit.returnPressed.connect(self.changepassfunction)

    def changepassfunction(self):
        password = self.PasslineEdit.text()
        self.accountinfo[0]["Pass"] = password
