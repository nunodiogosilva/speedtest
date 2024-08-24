import os
import json
from dotenv import load_dotenv
from grafana_api.grafana_face import GrafanaFace
from app.common.utils import Utils
from app.config.paths import Paths
from app.config.prometheus import Prometheus


class Grafana:

    PORT = 3000

    URL = f"http://localhost:{PORT}"

    CONFIGURATION_DIRECTORY = "/etc/grafana"

    CONFIGURATION_FILE = f"{CONFIGURATION_DIRECTORY}/grafana.ini"

    CONFIGURATION = """
#################################### Anonymous Auth ######################
[auth.anonymous]
# Enable anonymous access
enabled = true

# Organization name that should be used for unauthenticated users
org_name = Main Org.

# Role for unauthenticated users, other valid values are `Editor` and `Admin`
org_role = Viewer

# Hide the Grafana version text from the footer and help tooltip for unauthenticated users (default: false)
hide_version = true

# Setting this limits the number of anonymous devices in your instance. Any new anonymous devices added after the limit has been reached will be denied access.
device_limit = 3

"""

    DASHBOARDS_DIRECTORY = f"{Paths.PROJECT_DIRECTORY}/assets/dashboards"

    @classmethod
    def setup(cls, is_deployment=False):
        grafana = Grafana.connect()
        datasource = Grafana.update_datasources(grafana)
        Grafana.update_dashboards(grafana, datasource)

        print("\nChanging Grafana configuration file ownership...")
        if not Utils.has_terminal_output(["sudo", "chown", "-R", f"{Utils.os_username()}:root", Grafana.CONFIGURATION_DIRECTORY]):
            print("Unable to change Grafana configuration file ownership.")
        else:
            print("Successfully changed Grafana configuration file ownership.")

            Utils.create_file(Grafana.CONFIGURATION_FILE)
            with open(Grafana.CONFIGURATION_FILE, "r", encoding="utf-8") as file:
                content = file.read()
                if content == Grafana.CONFIGURATION:
                    if is_deployment:
                        print("\nRestarting Grafana...")
                        if not Utils.has_terminal_output(["sudo", "systemctl", "restart", "grafana-server"]):
                            print("Unable to restart Grafana.")
                        else:
                            print("Successfully restarted Grafana.")

                    print("\nGrafana is already configured.")
                else:
                    is_configured = True
                    print("\nUpdating Grafana configuration file...")
                    Utils.update_file(Grafana.CONFIGURATION_FILE,
                                      Grafana.CONFIGURATION, "w")
                    print("Successfully updated Grafana configuration file.")

                    print("\nRestarting Grafana...")
                    if not Utils.has_terminal_output(["sudo", "systemctl", "restart", "grafana-server"]):
                        is_configured = False
                        print("Unable to restart Grafana.")
                    else:
                        print("Successfully restarted Grafana.")

                    if not is_configured:
                        print("\nUnable to configure Grafana.")
                    else:
                        print("\nSuccessfully configured Grafana.")

    @classmethod
    def connect(cls):
        load_dotenv()
        grafana = GrafanaFace(
            auth=os.getenv("GRAFANA_API_TOKEN"),
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
