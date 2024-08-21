import time
import platform
import subprocess


class Network:

    def __init__(self):
        self.name = self.get_network_name()

    def get_network_name(self):
        os_name = platform.system()

        if os_name == "Windows":
            return self.get_network_name_windows()
        elif os_name == "Darwin":
            return self.get_network_name_macos()
        elif os_name == "Linux":
            return self.get_network_name_linux()
        else:
            return "N/A"

    def get_network_name_windows(self):
        network_name = None

        while network_name is None:
            try:
                output = subprocess.check_output(
                    ["netsh", "wlan", "show", "interfaces"], encoding='utf-8'
                )
                for line in output.split('\n'):
                    if "SSID" in line:
                        ssid = line.split(":")[1].strip()
                        if ssid:
                            network_name = ssid
                            print(f"Network: {network_name}")

            except subprocess.CalledProcessError as error:
                print(error)
                print("Retrying in 1 second...")
                time.sleep(1)

        return network_name

    def get_network_name_macos(self):
        network_name = None

        while network_name is None:
            try:
                output = subprocess.check_output(
                    ["networksetup", "-getairportnetwork", "en0"], encoding='utf-8'
                )
                if "Current Wi-Fi Network" in output:
                    network_name = output.split(": ")[1].strip()
                    print(f"Network: {network_name}")

            except subprocess.CalledProcessError as error:
                print(error)
                print("Retrying in 1 second...")
                time.sleep(1)

        return network_name

    def get_network_name_linux(self):
        network_name = None

        while network_name is None:
            try:
                output = subprocess.check_output(
                    ["iwgetid", "-r"], encoding='utf-8'
                )
                network_name = output.strip()
                print(f"Network: {network_name}")

            except subprocess.CalledProcessError as error:
                print(error)
                print("Retrying in 1 second...")
                time.sleep(1)

        return network_name
