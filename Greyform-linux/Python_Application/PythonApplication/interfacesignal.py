import psutil
import socket


def get_wireless_interfaces():
    # Get all network interfaces
    interfaces = psutil.net_if_addrs()
    
    # Ethernet interfaces typically start with 'e' or 'eth'
    ethernet_interfaces = {}
    for interface_name, interface_addresses in interfaces.items():
        for address in interface_addresses:
            # Check if the interface is of type AF_LINK (Ethernet) using socket.AF_PACKET for MAC address
            if address.family == socket.AF_PACKET:
                if interface_name.startswith('e') or interface_name.startswith('eth'):
                    ethernet_interfaces[interface_name] = {
                        "mac": address.address,  # MAC Address
                        "ip": None               # Default None for IP
                    }
            # Check if the address is of type IPv4 using socket.AF_INET
            if address.family == socket.AF_INET and interface_name in ethernet_interfaces:
                ethernet_interfaces[interface_name]["ip"] = address.address

    return ethernet_interfaces

def get_open_ports(interface_ip):
    open_ports = []
    # Iterate over all connections
    for conn in psutil.net_connections(kind='inet'):
        if conn.laddr and conn.laddr.ip == interface_ip:
            open_ports.append(conn.laddr.port)
    return open_ports

