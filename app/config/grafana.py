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
        datasource = Grafana.update_datasources(grafana)
        Grafana.update_dashboards(grafana, datasource)

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
            port=Grafana.PORT
        )

        return grafana

    @classmethod
    def get_datasource_by_name(cls, grafana, datasource_name):
        datasources = grafana.datasource.list_datasources()
        datasource = next(
            (datasource for datasource in datasources if datasource["name"] == datasource_name), None)

        return datasource

    @classmethod
    def update_datasources(cls, grafana):
        datasource = Grafana.get_datasource_by_name(
            grafana,
            Prometheus.DATASOURCE["name"]
        )

        if not datasource:
            print(
                f"\nCreating Grafana {Prometheus.DATASOURCE['name']} datasource...")
            grafana.datasource.create_datasource(Prometheus.DATASOURCE)

            datasource = Grafana.get_datasource_by_name(
                grafana,
                Prometheus.DATASOURCE["name"]
            )
            return datasource

        print(
            f"\nUpdating Grafana {Prometheus.DATASOURCE['name']} datasource...")
        grafana.datasource.update_datasource(
            datasource["id"],
            Prometheus.DATASOURCE
        )

        return datasource

    @classmethod
    def update_dashboard_json_datasource(cls, dashboard_json, datasource):
        panels = dashboard_json.get("panels", [])
        for panel in panels:
            if "datasource" in panel and panel["datasource"]["type"] == "prometheus":
                panel["datasource"]["uid"] = datasource["uid"]

            targets = panel.get("targets", [])
            for target in targets:
                if "datasource" in target and target["datasource"]["type"] == "prometheus":
                    target["datasource"]["uid"] = datasource["uid"]

        return dashboard_json

    @classmethod
    def update_dashboards(cls, grafana, datasource):
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
                    dashboard_json = Grafana.update_dashboard_json_datasource(
                        dashboard_json,
                        datasource
                    )

                    dashboard = {
                        "dashboard": dashboard_json,
                        "overwrite": True
                    }
                    grafana.dashboard.update_dashboard(dashboard)
