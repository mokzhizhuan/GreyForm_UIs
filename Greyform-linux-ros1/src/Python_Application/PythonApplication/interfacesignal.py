import psutil
import socket
import subprocess
import re
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


#get all wireless interface
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

#include active wifi as main
def get_active_wifi_interface():
    result = subprocess.run(["ip", "addr", "show"], capture_output=True, text=True)
    interface_pattern = re.compile(r"\d+: (\w+):.*state UP")
    ip_pattern = re.compile(r"\s+inet (\d+\.\d+\.\d+\.\d+)/\d+")
    active_interface = None
    ip_address = None
    for line in result.stdout.splitlines():
        interface_match = interface_pattern.match(line)
        if interface_match:
            active_interface = interface_match.group(1).strip()
        ip_match = ip_pattern.match(line)
        if ip_match and active_interface:
            ip_address = ip_match.group(1).strip()
            host, port = get_open_ports(ip_address)
            return active_interface, ip_address, host, port
    return None, None, None, None

#check for one open port and set it as active
def get_open_ports(interface_ip):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((interface_ip, 0))
    host, port = s.getsockname()
    s.close()
    return host, port

#get default gateway from ip
def get_default_gateway():
    try:
        route_result = subprocess.run(["ip", "route"], capture_output=True, text=True)
        for line in route_result.stdout.splitlines():
            if line.startswith("default via"):
                return line.split()[2]
    except Exception as e:
        print(f"Error fetching default gateway: {e}")
    return None

#get dns server
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

#show interface as setting
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

#show all interface in tree widget
def show_interface(interfaces, treeWidget):
    if interfaces:
        group_item = QTreeWidgetItem(treeWidget)
        group_item.setText(0, "Ethernet Interfaces")
        for interface in interfaces:
            item = QTreeWidgetItem(group_item)
            item.setText(0, interface)
    else:
        no_ethernet_item = QTreeWidgetItem(treeWidget)
        no_ethernet_item.setText(0, "No Ethernet Interfaces found.")
