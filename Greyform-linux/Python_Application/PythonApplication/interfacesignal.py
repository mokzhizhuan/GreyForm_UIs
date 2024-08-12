import psutil
import socket
import subprocess

def get_wireless_interfaces():
    interfaces = psutil.net_if_addrs()
    stats = psutil.net_if_stats()

    ethernet_interfaces = {}
    for interface_name, interface_addresses in interfaces.items():
        if interface_name.startswith('e') or interface_name.startswith('eth'):
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
                ethernet_interfaces[interface_name]["link_speed"] = stats[interface_name].speed

    return ethernet_interfaces

def get_open_ports(interface_ip):
    open_ports = []
    for conn in psutil.net_connections(kind='inet'):
        if conn.laddr and conn.laddr.ip == interface_ip:
            open_ports.append(conn.laddr.port)
    return open_ports[0]

def get_default_gateway():
    try:
        route_result = subprocess.run(['ip', 'route'], capture_output=True, text=True)
        for line in route_result.stdout.splitlines():
            if line.startswith('default via'):
                return line.split()[2]
    except Exception as e:
        print(f"Error fetching default gateway: {e}")
    return None

def get_dns_servers():
    dns_servers = []
    try:
        with open('/etc/resolv.conf', 'r') as resolv_file:
            for line in resolv_file:
                if line.startswith('nameserver'):
                    dns_servers.append(line.split()[1])
    except Exception as e:
        print(f"Error reading DNS servers: {e}")
    return dns_servers

