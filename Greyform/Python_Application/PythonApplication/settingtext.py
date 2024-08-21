from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from pywifi import PyWiFi, const
import datetime
import socket
import netifaces as ni
import subprocess
import re
from pywifi import PyWiFi


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
        SystemDate,
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
        self.SystemDate = SystemDate
        self.PasslineEdit = PasslineEdit
        self.userlabel = userlabel
        self.accountinfo = accountinfo
        self.retranslateUi()        
    
    def get_active_wifi_interface(self):
        result = subprocess.run(['ipconfig'], capture_output=True, text=True)
        interface_pattern = re.compile(r"Wireless LAN adapter (.+):")
        ip_pattern = re.compile(r"\s+IPv4 Address.*:\s*(.+)")
        active_interface = None
        ip_address = None
        for line in result.stdout.splitlines():
            interface_match = interface_pattern.match(line)
            if interface_match:
                active_interface = interface_match.group(1).strip()
            ip_match = ip_pattern.match(line)
            if ip_match and active_interface:
                ip_address = ip_match.group(1).strip()
                return ip_address
        return ip_address
        
    def get_open_port_and_host(self, ip_address):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((ip_address, 0)) 
        host, port = s.getsockname()  
        s.close()
        return host, port

    # add text
    def retranslateUi(self):
        ip_address = self.get_active_wifi_interface()
        self.labeltitlsetting.setText("<h3>Setting</h3>")
        self.ip_label.setText(f"IP Address: {ip_address}")
        host, port = self.get_open_port_and_host(ip_address)
        self.titlelabel.setText("<h3>About My Application</h3>")
        self.info_label.setText("This is a Robot Marking Application program")
        self.version_label.setText("Version: 1.0")
        self.author_label.setText("Created by Mok Zhi Zhuan")
        self.Portnumipadd.setText(f"Port: {port}")
        self.host.setText(f"Host: {host}")
        datetoday = datetime.date.today()
        datetodayformatted = (
            f"{datetoday.day}/{datetoday.month}/{datetoday.strftime('%y')}"
        )
        self.SystemDate.setText(f"Date : {datetodayformatted}")
        self.userlabel.setText(f"<h2>User: {self.accountinfo[0]['UserID']}</h2>")
        self.PasslineEdit.setText(f"{self.accountinfo[0]['Pass']}")
        self.PasslineEdit.returnPressed.connect(self.changepassfunction)

    def changepassfunction(self):
        password = self.PasslineEdit.text()
        self.accountinfo[0]["Pass"] = password
