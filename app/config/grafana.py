import os
from dotenv import load_dotenv
from grafana_api.grafana_face import GrafanaFace
from app.common.utils import Utils
from app.config.paths import Paths


class Grafana:

    def __init__(self):
        load_dotenv()
        self.hostname = Utils.os_hostname()
        self.service_name = "grafana-server"
        self.service_description = "Grafana"
        self.config = os.getenv("GRAFANA_CONFIG_PATH")
        self.templates = f"{Paths.TEMPLATES_DIRECTORY}/grafana"
        self.config_template = f"{self.templates}/grafana.ini"
        self.connection = self.connect(
            os.getenv("GRAFANA_API_TOKEN"),
            self.hostname,
            int(os.getenv("GRAFANA_PORT"))
        )
        self.datasource = {
            "name": "Prometheus",
            "type": "prometheus",
            "url": os.getenv("PROMETHEUS_URL"),
            "access": "proxy",
            "basicAuth": False,
            "isDefault": True,
            "jsonData": {
                "httpMethod": "POST"
            }
        }
        self.dashboards = f"{self.templates}/dashboards"

    def setup(self, is_deployment=False):
        Utils.create_file(self.config)
        config_content = Utils.get_file_content(self.config)
        config_template_content = Utils.get_file_content(self.config_template)
        if config_content == config_template_content:
            print("Grafana is already configured.")

            if is_deployment:
                Utils.restart_service(self.service_name, self.service_description)
        else:
            print("Updating Grafana configuration file...")
            Utils.update_file(self.config, config_template_content, "w")
            print("Successfully updated Grafana configuration file.")

            if is_deployment:
                Utils.restart_service(self.service_name, self.service_description)
            else:
                Utils.reload_service(self.service_name, self.service_description)

        datasource = self.update_datasource()
        self.update_dashboards(datasource)

    def connect(self, api_token, host, port):
        connection = GrafanaFace(
            auth=api_token,
            host=host,
            port=port
        )

        return connection

    def get_datasource_by_name(self, name):
        datasources = self.connection.datasource.list_datasources()
        datasource = next((datasource for datasource in datasources
                           if datasource["name"] == name), None)
        return datasource

    def update_datasource(self):
        datasource = self.get_datasource_by_name(self.datasource["name"])

        if not datasource:
            print(f"Creating Grafana {self.datasource['name']} datasource...")
            self.connection.datasource.create_datasource(self.datasource)
            datasource = self.get_datasource_by_name(self.datasource["name"])
            return datasource

        print(f"Updating Grafana {self.datasource['name']} datasource...")
        self.connection.datasource.update_datasource(datasource["id"], self.datasource)
        return datasource

    def update_dashboard_datasource(self, dashboard, datasource):
        if dashboard["panels"]:
            for panel in dashboard["panels"]:
                if "datasource" in panel and panel["datasource"]["type"] == "prometheus":
                    panel["datasource"]["uid"] = datasource["uid"]

                if panel["targets"]:
                    for target in panel["targets"]:
                        if "datasource" in target and target["datasource"]["type"] == "prometheus":
                            target["datasource"]["uid"] = datasource["uid"]

        if dashboard["templating"]["list"]:
            for item in dashboard["templating"]["list"]:
                if "datasource" in item and item["datasource"]["type"] == "prometheus":
                    item["datasource"]["uid"] = datasource["uid"]
        return dashboard

    def update_dashboards(self, datasource):
        print("Creating and updating Grafana dashboards...")
        for filename in os.listdir(self.dashboards):
            dashboard = Utils.get_file_content(f"{self.dashboards}/{filename}")
            if not dashboard:
                print(f"Couldn't load Grafana dashboard {filename} file.")
            else:
                updated_dashboard = self.update_dashboard_datasource(dashboard, datasource)
                dashboard = {
                    "dashboard": updated_dashboard,
                    "overwrite": True
                }
                self.connection.dashboard.update_dashboard(dashboard)
