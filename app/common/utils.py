import os
import time
import socket
import platform
import subprocess
import json
import yaml
from jinja2 import Environment, FileSystemLoader


class Utils:

    @staticmethod
    def os_hostname():
        return socket.gethostname()

    @staticmethod
    def os_network():
        os_name = platform.system()

        if os_name == "Darwin":
            return Utils.get_os_network_macos()

        if os_name == "Linux":
            return Utils.get_os_network_linux()
        return "N/A"

    @staticmethod
    def get_os_network_macos():
        network = None

        while network is None:
            try:
                output = Utils.get_terminal_output(
                    ["networksetup", "-getairportnetwork", "en0"])
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
                output = Utils.get_terminal_output(["iwgetid", "-r"])
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
            if file.endswith(".json"):
                json.dump(content, updated_file, indent=4)
            elif file.endswith(".yml") or file.endswith(".yaml"):
                yaml.dump(content, updated_file, default_flow_style=False)
            else:
                updated_file.write(content)

        if permission:
            os.chmod(file, int(f"0o{permission}", 8))

    @staticmethod
    def get_file_content(file):
        if os.path.exists(file):
            with open(file, "r", encoding="utf-8") as file_content:
                if file.endswith(".json"):
                    return json.load(file_content)
                if file.endswith(".yml") or file.endswith(".yaml"):
                    return yaml.safe_load(file_content)
                return file_content.read()
        return False

    @staticmethod
    def get_template_content(directory, file, args):
        template_directory = Environment(
            loader=FileSystemLoader(directory)
        )
        template_file = template_directory.get_template(file)
        template_content = template_file.render(args)
        return template_content

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

    @staticmethod
    def start_service(name, description):
        print(f"Starting {description}...")
        if not Utils.has_terminal_output(["sudo", "systemctl", "start", name]):
            print(f"Unable to start {description}.")
            return False
        print(f"Successfully started {description}.")
        return True

    @staticmethod
    def stop_service(name, description):
        print(f"Stopping {description}...")
        if not Utils.has_terminal_output(["sudo", "systemctl", "stop", name]):
            print(f"Unable to stop {description}.")
            return False
        print(f"Successfully stopped {description}.")
        return True

    @staticmethod
    def restart_service(name, description):
        print(f"Restarting {description}...")
        if not Utils.has_terminal_output(["sudo", "systemctl", "restart", name]):
            print(f"Unable to restart {description}.")
            return False
        print(f"Successfully restarted {description}.")
        return True

    @staticmethod
    def enable_service(name, description):
        print(f"Enabling {description}...")
        if not Utils.has_terminal_output(["sudo", "systemctl", "enable", name]):
            print(f"Unable to enable {description}.")
            return False
        print(f"Successfully enabled {description}.")
        return True

    @staticmethod
    def reload_service(name, description):
        print("Reloading Systemd files...")
        if not Utils.has_terminal_output(["sudo", "systemctl", "daemon-reload"]):
            print("Unable to reload Systemd files.")
        else:
            print("Successfully reloaded Systemd files.")

            if Utils.enable_service(name, description):
                Utils.start_service(name, description)
