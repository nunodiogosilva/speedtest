from prometheus_client import start_http_server
from app.common.utils import Utils


class Prometheus:

    PORT = 9090

    URL = f"http://localhost:{PORT}"

    NODE_PORT = 9100

    METRICS_PORT = 8000

    CONFIGURATION_FILE = "/etc/prometheus/prometheus.yml"

    CONFIGURATION = f"""
# Global configuration
global:
  scrape_interval: 15s # How often to scrape metrics (default is 1m)
  evaluation_interval: 15s # How often to evaluate rules (default is 1m)

# A scrape configuration containing endpoints to scrape.
scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:{PORT}']

  - job_name: 'node'
    static_configs:
      - targets: ['localhost:{NODE_PORT}']

  - job_name: 'metrics'
    static_configs:
      - targets: ['localhost:{METRICS_PORT}']
"""

    DATASOURCE = {
        "name": "Prometheus",
        "type": "prometheus",
        "url": URL,
        "access": "proxy",
        "basicAuth": False,
        "isDefault": True,
        "jsonData": {
            "httpMethod": "POST"
        }
    }

    @classmethod
    def setup(cls, is_deployment=False):
        if not Utils.has_terminal_output(["sudo", "prometheus", "--version"]):
            is_installed = True
            print("\nInstalling Prometheus...")
            if not Utils.has_terminal_input(["sudo", "apt-get", "install", "prometheus", "-y"]):
                is_installed = False
            else:
                print("\nCreating Prometheus configuration file...")
                Utils.create_file(Prometheus.CONFIGURATION_FILE)
                print("Successfully created Prometheus configuration file.")

                print("\nChanging Prometheus configuration file ownership...")
                if not Utils.has_terminal_output(["sudo", "chown", "-R", f"{Utils.username()}:root", Prometheus.CONFIGURATION_FILE]):
                    print("Unable to change Prometheus configuration file ownership.")
                else:
                    print("Successfully changed Prometheus configuration file ownership.")

                    print("\nUpdating Prometheus configuration file...")
                    Utils.update_file(Prometheus.CONFIGURATION_FILE,
                                    Prometheus.CONFIGURATION, "w")
                    print("Successfully updated Prometheus configuration file.")

                    print("\nEnabling Prometheus...")
                    if not Utils.has_terminal_output(["sudo", "systemctl", "enable", "prometheus"]):
                        is_installed = False
                        print("Unable to enable Prometheus.")
                    else:
                        print("Successfully enabled Prometheus.")

                        print("\nStarting Prometheus...")
                        if not Utils.has_terminal_output(["sudo", "systemctl", "start", "prometheus"]):
                            is_installed = False
                            print("Unable to start Prometheus.")
                        else:
                            print("Successfully started Prometheus.")

            if not is_installed:
                print("Unable to install Prometheus.")
            else:
                print("Successfully installed Prometheus.")
        else:
            print("Prometheus is already installed.")

            with open(Prometheus.CONFIGURATION_FILE, "r", encoding="utf-8") as file:
                content = file.read()
                if content == Prometheus.CONFIGURATION:
                    if is_deployment:
                        print("\nRestarting Prometheus...")
                        if not Utils.has_terminal_output(["sudo", "systemctl", "restart", "prometheus"]):
                            print("Unable to restart Prometheus.")
                        else:
                            print("Successfully restarted Prometheus.")

                    print("Prometheus is already configured.")
                else:
                    is_configured = True
                    print("\nChanging Prometheus configuration file ownership...")
                    if not Utils.has_terminal_output(["sudo", "chown", "-R", f"{Utils.username()}:root", Prometheus.CONFIGURATION_FILE]):
                        is_configured = False
                        print("Unable to change Prometheus configuration file ownership.")
                    else:
                        print("Successfully changed Prometheus configuration file ownership.")
                        print("\nUpdating Prometheus configuration file...")
                        Utils.update_file(Prometheus.CONFIGURATION_FILE,
                                        Prometheus.CONFIGURATION, "w")
                        print("Successfully updated Prometheus configuration file.")

                        print("\nRestarting Prometheus...")
                        if not Utils.has_terminal_output(["sudo", "systemctl", "restart", "prometheus"]):
                            is_configured = False
                            print("Unable to restart Prometheus.")
                        else:
                            print("Successfully restarted Prometheus.")

                    if not is_configured:
                        print("Unable to configure Prometheus.")
                    else:
                        print("Successfully configured Prometheus.")

    @classmethod
    def start_server(cls):
        start_http_server(Prometheus.METRICS_PORT)
