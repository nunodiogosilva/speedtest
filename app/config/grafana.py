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
