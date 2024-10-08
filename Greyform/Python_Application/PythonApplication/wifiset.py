from PyQt5 import QtCore, QtWidgets, QtGui, uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from pywifi import PyWiFi

#setup wifi interface for setting implementation
class setup_wifi(object):
    def __init__(self, treeWidget, interface_label):
        # starting initialize
        super().__init__()
        self.wifi = PyWiFi()
        self.interface = self.wifi.interfaces()[0]
        self.treeWidget = treeWidget
        self.interface_label = interface_label
        self.refreshWiFiList()

    def refreshWiFiList(self):
        networks = self.interface.scan_results()
        self.treeWidget.clear()
        ssid = networks[0].ssid
        signal_strength = networks[0].signal
        item = QTreeWidgetItem([ssid, str(signal_strength)])
        self.treeWidget.addTopLevelItem(item)
        interface_info = f"Interface: {self.interface.name()}"
        self.interface_label.setText(interface_info)
