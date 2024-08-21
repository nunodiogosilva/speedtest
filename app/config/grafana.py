import os
import json
import getpass
from grafana_api.grafana_face import GrafanaFace
from app.common.utils import Utils
from app.config.paths import Paths
from app.config.prometheus import Prometheus


class Grafana:

    PORT = 3000

    URL = f"http://localhost:{PORT}"

    DASHBOARDS_DIRECTORY = f"{Paths.PROJECT_DIRECTORY}/assets/dashboards"

    @classmethod
    def setup(cls, is_deployment=False):
        if not Utils.has_terminal_output(["sudo", "grafana-server", "--version"]):
            print("\nInstalling prerequisite packages...")
            if not Utils.has_terminal_input(["sudo", "apt-get", "install", "-y", "apt-transport-https", "software-properties-common", "wget"]):
                print("Unable to install prerequisite packages.")
            else:
                print("Successfully installed prerequisite packages.")

                print("\nCreating /etc/apt/keyrings/ directory...")
                if not Utils.has_terminal_output(["sudo", "mkdir", "-p", "/etc/apt/keyrings/"]):
                    print("Unable to create /etc/apt/keyrings/ directory.")
                else:
                    print("Successfully created /etc/apt/keyrings/ directory.")

                    print("\nImporting GPG key...")
                    if not Utils.has_terminal_output(["sudo", "wget", "-q", "-O", "-", "https://apt.grafana.com/gpg.key", "|", "gpg --dearmor", "|", "sudo", "tee", "/etc/apt/keyrings/grafana.gpg", ">", "/dev/null"]):
                        print("Unable to import GPG key.")
                    else:
                        print("Successfully created /etc/apt/keyrings/ directory.")

                        print("\nAdding stable releases repository...")
                        if not Utils.has_terminal_output(["sudo", "echo", '"deb [signed-by=/etc/apt/keyrings/grafana.gpg] https://apt.grafana.com stable main"', "|", "sudo", "tee", "-a", "/etc/apt/sources.list.d/grafana.list"]):
                            print("Unable to add stable releases repository.")
                        else:
                            print("Successfully added stable releases repository.")

                            print("\nUpdating packages...")
                            if not Utils.has_terminal_input(["sudo", "apt-get", "update"]):
                                print("Unable to update packages.")
                            else:
                                print("Successfully updated packages.")

                                print("\nInstalling Grafana...")
                                if not Utils.has_terminal_input(["sudo", "apt-get", "install", "grafana"]):
                                    print("Unable to install Grafana.")
                                else:
                                    print("Successfully installed Grafana.")

                                    print("\nEnabling Grafana...")
                                    if not Utils.has_terminal_output(["sudo", "systemctl", "enable", "grafana-server"]):
                                        print("Unable to enable Grafana.")
                                    else:
                                        print("Successfully enabled Grafana.")

                                        print("\nStarting Grafana...")
                                        if not Utils.has_terminal_output(["sudo", "systemctl", "start", "grafana-server"]):
                                            print("Unable to start Grafana.")
                                        else:
                                            print("Successfully started Grafana.")

                                            grafana = Grafana.connect()
                                            Grafana.update_datasources(grafana)
                                            Grafana.update_dashboards(grafana)
        else:
            print("Grafana is already installed.")

            grafana = Grafana.connect()
            Grafana.update_datasources(grafana)
            Grafana.update_dashboards(grafana)

        if is_deployment:
            print("\nRestarting Grafana...")
            if not Utils.has_terminal_output(["sudo", "systemctl", "restart", "grafana-server"]):
                print("Unable to restart Grafana.")
            else:
                print("Successfully restarted Grafana.")

    @classmethod
    def connect(cls):
        print(
            f"\nGet Grafana Service Account Token at {Grafana.URL}/org/serviceaccounts .")
        api_token = getpass.getpass(
            "Enter your Grafana Service Account Token:\n>")

        grafana = GrafanaFace(
            auth=api_token,
            host=Prometheus.URL
        )

        return grafana

    @classmethod
    def update_datasources(cls, grafana):
        datasources = grafana.datasource.list_datasources()
        datasource = next(
            (datasource for datasource in datasources if datasource['name'] == Prometheus.DATASOURCE['name']), None)

        if not datasource:
            print(
                f"\nCreating Grafana {Prometheus.DATASOURCE['name']} datasource...")
            grafana.datasource.create_datasource(Prometheus.DATASOURCE)
        else:
            print(
                f"\nUpdating Grafana {Prometheus.DATASOURCE['name']} datasource...")
            grafana.datasource.update_datasource(
                datasource['id'], Prometheus.DATASOURCE)

    @classmethod
    def update_dashboards(cls, grafana):
        print("\nCreating and updating Grafana dashboards...")
        for filename in os.listdir(Grafana.DASHBOARDS_DIRECTORY):
            if filename.endswith(".json"):
                dashboard_file = os.path.join(
                    Grafana.DASHBOARDS_DIRECTORY, filename)

                dashboard_json = None
                with open(dashboard_file, "r", encoding="utf-8") as file:
                    dashboard_json = json.load(file)

                if not dashboard_json:
                    print(f"Couldn't load Grafana dashboard {filename} file.")
                else:
                    dashboard = {
                        "dashboard": dashboard_json,
                        "overwrite": True
                    }
                    grafana.dashboard.update_dashboard(dashboard)
