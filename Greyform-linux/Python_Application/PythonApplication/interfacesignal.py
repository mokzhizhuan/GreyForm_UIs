import subprocess
import re


def get_wireless_interfaces():
    try:
        # Use nmcli to list all devices
        result = subprocess.run(
            ["nmcli", "device", "status"], capture_output=True, text=True, check=True
        )
        wireless_interfaces = []
        for line in result.stdout.split("\n"):
            if "wifi" in line:
                columns = line.split()
                if len(columns) > 0:
                    wireless_interfaces.append(columns[0])
        return wireless_interfaces
    except subprocess.CalledProcessError as e:
        print(f"Command failed with error: {e}")
        return []


def get_signal_strength(interface):
    try:
        result = subprocess.run(
            ["iwconfig", interface], capture_output=True, text=True, check=True
        )
        for line in result.stdout.split("\n"):
            if "Signal level" in line:
                match = re.search(r"Signal level=(-?\d+)", line)
                if match:
                    return match.group(1)
    except subprocess.CalledProcessError as e:
        print(f"Command failed with error: {e}")
    return None
