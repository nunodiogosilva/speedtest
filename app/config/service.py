from app.common.utils import Utils
from app.config.paths import Paths
from app.config.python import Python


class Service:

    NAME = "speedtest"

    DESCRIPTION = "Speedtest Service"

    CONFIGURATION_DIRECTORY = "/etc/systemd/system"

    CONFIGURATION_FILE = f"{CONFIGURATION_DIRECTORY}/{NAME}.service"

    CONFIGURATION = f"""
[Unit]
Description={DESCRIPTION}
After=network.target

[Service]
EnvironmentFile={Paths.ENVIRONMENT_FILE}
WorkingDirectory={Paths.PROJECT_DIRECTORY}
ExecStart={Paths.BASH_INTERPRETER_FILE} -c "cd {Paths.PROJECT_DIRECTORY} && {Python.INTERPRETER_FILE} -m app.run"
Restart=always

[Install]
WantedBy=multi-user.target
"""

    @classmethod
    def setup(cls, is_deployment=False):
        Utils.create_file(Service.CONFIGURATION_FILE)
        with open(Service.CONFIGURATION_FILE, "r", encoding="utf-8") as file:
            content = file.read()
            if content == Service.CONFIGURATION:
                if is_deployment:
                    print(
                        f"Restarting {Service.DESCRIPTION} Systemd service...")
                    if not Utils.has_terminal_output(["sudo", "systemctl", "restart", f"{Service.NAME}.service"]):
                        is_installed = False
                        print(
                            f"Unable to restart {Service.DESCRIPTION} Systemd service.")
                    else:
                        print(
                            f"Successfully restarted {Service.DESCRIPTION} Systemd service.")

                print(f"{Service.DESCRIPTION} Systemd service is already installed.")
            else:
                is_installed = True
                print(f"Installing {Service.DESCRIPTION} Systemd service...")
                Utils.update_file(Service.CONFIGURATION_FILE,
                                  Service.CONFIGURATION, "w")

                print("Reloading Systemd files...")
                if not Utils.has_terminal_output(["sudo", "systemctl", "daemon-reload"]):
                    print("Unable to reload Systemd files.")
                    is_installed = False
                else:
                    print("Successfully reloaded Systemd files.")

                    print(f"Enabling {Service.DESCRIPTION} Systemd service...")
                    if not Utils.has_terminal_output(["sudo", "systemctl", "enable", f"{Service.NAME}.service"]):
                        is_installed = False
                        print(
                            f"Unable to enable {Service.DESCRIPTION} Systemd service.")
                    else:
                        print(
                            f"Successfully enabled {Service.DESCRIPTION} Systemd service.")

                        print(
                            f"Starting {Service.DESCRIPTION} Systemd service...")
                        if not Utils.has_terminal_output(["sudo", "systemctl", "start", f"{Service.NAME}.service"]):
                            is_installed = False
                            print(
                                f"Unable to start {Service.DESCRIPTION} Systemd service.")
                        else:
                            print(
                                f"Successfully started {Service.DESCRIPTION} Systemd service.")

                if not is_installed:
                    print(
                        f"Unable to install {Service.DESCRIPTION} Systemd service.")
                else:
                    print(
                        f"Successfully installed {Service.DESCRIPTION} Systemd service.")
