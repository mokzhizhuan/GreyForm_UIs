import psutil
import socket
import subprocess
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


def get_wireless_interfaces():
    interfaces = psutil.net_if_addrs()
    stats = psutil.net_if_stats()
    ethernet_interfaces = {}
    for interface_name, interface_addresses in interfaces.items():
        if interface_name.startswith("e") or interface_name.startswith("eth"):
            ethernet_interfaces[interface_name] = {
                "mac": None,
                "ipv4": None,
                "ipv6": None,
                "link_speed": None,
            }
            for address in interface_addresses:
                if address.family == socket.AF_PACKET:
                    ethernet_interfaces[interface_name]["mac"] = address.address
                if address.family == socket.AF_INET:
                    ethernet_interfaces[interface_name]["ipv4"] = address.address
                if address.family == socket.AF_INET6:
                    ethernet_interfaces[interface_name]["ipv6"] = address.address
            if interface_name in stats:
                ethernet_interfaces[interface_name]["link_speed"] = stats[
                    interface_name
                ].speed
    return ethernet_interfaces


def get_open_ports(interface_ip):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((interface_ip, 0))
    host, port = s.getsockname()
    s.close()
    return host, port


def get_default_gateway():
    try:
        route_result = subprocess.run(["ip", "route"], capture_output=True, text=True)
        for line in route_result.stdout.splitlines():
            if line.startswith("default via"):
                return line.split()[2]
    except Exception as e:
        print(f"Error fetching default gateway: {e}")
    return None


def get_dns_servers():
    dns_servers = []
    try:
        with open("/etc/resolv.conf", "r") as resolv_file:
            for line in resolv_file:
                if line.startswith("nameserver"):
                    dns_servers.append(line.split()[1])
    except Exception as e:
        print(f"Error reading DNS servers: {e}")
    return dns_servers


def get_interface(interfaces, interfaces_name):
    interface_details = interfaces.get(interfaces_name, {})
    ip_address = interface_details.get("ipv4", "N/A")
    host = None
    if ip_address:
        host, open_ports = get_open_ports(ip_address)
        ports_text = open_ports
    else:
        ports_text = "N/A"
    interface_info = f"Interface: {interfaces_name}"
    return interface_info, ip_address, host, ports_text


def show_interface(interfaces, interface_label, treeWidget):
    interface_info = "Interface: None"
    interface_label.setText(interface_info)
    if interfaces:
        group_item = QTreeWidgetItem(treeWidget)
        group_item.setText(0, "Ethernet Interfaces")
        for interface in interfaces:
            item = QTreeWidgetItem(group_item)
            item.setText(0, interface)
    else:
        no_ethernet_item = QTreeWidgetItem(treeWidget)
        no_ethernet_item.setText(0, "No Ethernet Interfaces found.")
