import os
import time
import platform
import subprocess
from dotenv import load_dotenv


class Utils:

    @staticmethod
    def os_username():
        load_dotenv()
        return os.getenv("OS_USERNAME")

    @staticmethod
    def os_network():
        os_name = platform.system()

        if os_name == "Windows":
            return Utils.get_os_network_windows()

        if os_name == "Darwin":
            return Utils.get_os_network_macos()

        if os_name == "Linux":
            return Utils.get_os_network_linux()

        return "N/A"

    @staticmethod
    def get_os_network_windows():
        network = None

        while network is None:
            try:
                output = subprocess.check_output(
                    ["netsh", "wlan", "show", "interfaces"], encoding='utf-8'
                )
                for line in output.split('\n'):
                    if "SSID" in line:
                        ssid = line.split(":")[1].strip()
                        if ssid:
                            network = ssid
                            print(f"Network: {network}")

            except subprocess.CalledProcessError as error:
                print(error)
                print("Retrying in 1 second...")
                time.sleep(1)

        return network

    @staticmethod
    def get_os_network_macos():
        network = None

        while network is None:
            try:
                output = subprocess.check_output(
                    ["networksetup", "-getairportnetwork", "en0"], encoding='utf-8'
                )
                if "Current Wi-Fi Network" in output:
                    network = output.split(": ")[1].strip()
                    print(f"Network: {network}")

            except subprocess.CalledProcessError as error:
                print(error)
                print("Retrying in 1 second...")
                time.sleep(1)

        return network

    @staticmethod
    def get_os_network_linux():
        network = None

        while network is None:
            try:
                output = subprocess.check_output(
                    ["iwgetid", "-r"], encoding='utf-8'
                )
                network = output.strip()
                print(f"Network: {network}")

            except subprocess.CalledProcessError as error:
                print(error)
                print("Retrying in 1 second...")
                time.sleep(1)

        return network

    @staticmethod
    def create_file(file, content="", permission=None):
        if not os.path.exists(file):
            with open(file, "w", encoding="utf-8") as created_file:
                created_file.write(content)

            if permission:
                os.chmod(file, int(f"0o{permission}", 8))

    @staticmethod
    def update_file(file, content, update_type, permission=None):
        with open(file, update_type, encoding="utf-8") as updated_file:
            updated_file.write(content)

        if permission:
            os.chmod(file, int(f"0o{permission}", 8))

    @staticmethod
    def has_terminal_output(command: list):
        try:
            subprocess.check_output(command)
            return True

        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    @staticmethod
    def get_terminal_output(command: list):
        try:
            return subprocess.check_output(command, text=True)

        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    @staticmethod
    def has_terminal_input(command: list):
        try:
            subprocess.check_call(command)
            return True

        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
