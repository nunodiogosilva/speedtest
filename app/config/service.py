from app.common.utils import Utils
from app.config.paths import Paths


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
ExecStart={Paths.BASH_INTERPRETER_FILE} -c "cd {Paths.PROJECT_DIRECTORY} && {Paths.PYTHON_INTERPRETER_FILE} -m app.run"
Restart=always

[Install]
WantedBy=multi-user.target
"""

    @classmethod
    def setup(cls, is_deployment=False):
        print(
            f"\nChanging {Service.DESCRIPTION} Systemd service configuration file ownership...")
        if not Utils.has_terminal_output(["sudo", "chown", "-R", f"{Utils.username()}:root", Service.CONFIGURATION_DIRECTORY]):
            print(
                f"Unable to change {Service.DESCRIPTION} Systemd service configuration file ownership.")
        else:
            print(
                f"Successfully changed {Service.DESCRIPTION} Systemd service configuration file ownership.")

            print(
                f"\nCreating {Service.DESCRIPTION} Systemd service configuration file...")
            Utils.create_file(Service.CONFIGURATION_FILE)
            print(
                f"Successfully created {Service.DESCRIPTION} Systemd service configuration file.")

            with open(Service.CONFIGURATION_FILE, "r", encoding="utf-8") as file:
                content = file.read()
                if content == Service.CONFIGURATION:
                    if is_deployment:
                        print(
                            f"\nRestarting {Service.DESCRIPTION} Systemd service...")
                        if not Utils.has_terminal_output(["sudo", "systemctl", "restart", f"{Service.NAME}.service"]):
                            print(
                                f"Unable to restart {Service.DESCRIPTION} Systemd service.")
                        else:
                            print(
                                f"Successfully restarted {Service.DESCRIPTION} Systemd service.")

                    print(
                        f"{Service.DESCRIPTION} Systemd service is already configured.")
                else:
                    is_configured = True
                    print(
                        f"\nUpdating {Service.DESCRIPTION} Systemd service configuration file...")
                    Utils.update_file(Service.CONFIGURATION_FILE,
                                      Service.CONFIGURATION, "w")
                    print(
                        f"Successfully updated {Service.DESCRIPTION} Systemd service configuration file.")

                    print("\nReloading Systemd files...")
                    if not Utils.has_terminal_output(["sudo", "systemctl", "daemon-reload"]):
                        print("Unable to reload Systemd files.")
                        is_configured = False
                    else:
                        print("Successfully reloaded Systemd files.")

                        print(
                            f"\nEnabling {Service.DESCRIPTION} Systemd service...")
                        if not Utils.has_terminal_output(["sudo", "systemctl", "enable", f"{Service.NAME}.service"]):
                            is_configured = False
                            print(
                                f"Unable to enable {Service.DESCRIPTION} Systemd service.")
                        else:
                            print(
                                f"Successfully enabled {Service.DESCRIPTION} Systemd service.")

                            print(
                                f"\nStarting {Service.DESCRIPTION} Systemd service...")
                            if not Utils.has_terminal_output(["sudo", "systemctl", "start", f"{Service.NAME}.service"]):
                                is_configured = False
                                print(
                                    f"Unable to start {Service.DESCRIPTION} Systemd service.")
                            else:
                                print(
                                    f"Successfully started {Service.DESCRIPTION} Systemd service.")

                    if not is_configured:
                        print(
                            f"Unable to configure {Service.DESCRIPTION} Systemd service.")
                    else:
                        print(
                            f"Successfully configured {Service.DESCRIPTION} Systemd service.")
