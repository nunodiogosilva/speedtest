import os
import re
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

    CONFIGURATION_SECTIONS = [
        {
            "section": "auth.anonymous",
            "content": """
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
        }
    ]

    DASHBOARDS_DIRECTORY = f"{Paths.PROJECT_DIRECTORY}/assets/dashboards"

    @classmethod
    def setup(cls, is_deployment=False):
        grafana = Grafana.connect()
        datasource = Grafana.update_datasources(grafana)
        Grafana.update_dashboards(grafana, datasource)
        Grafana.update_configuration(is_deployment)

    @classmethod
    def restart(cls):
        print("\nRestarting Grafana...")
        if not Utils.has_terminal_output(["sudo", "systemctl", "restart", "grafana-server"]):
            print("Unable to restart Grafana.")
        else:
            print("Successfully restarted Grafana.")

    @classmethod
    def update_section(cls, file, section, content):
        # Read the existing content of the file
        with open(file, "r", encoding="utf-8") as config_file:
            config_file_content = config_file.read()

        # Define the regex pattern to find the specified section and its content
        pattern = re.compile(rf'\[{re.escape(section)}\][\s\S]*?(?=\[|\Z)', re.MULTILINE)
        match = pattern.search(config_file_content)

        # Format the new section content with proper section header
        new_section = f'[{section}]\n{content.strip()}'

        if match:
            # Replace the existing section with the new content
            updated_content = re.sub(
                rf'\[{re.escape(section)}\][\s\S]*?(?=\[|\Z)',
                new_section,
                config_file_content,
                flags=re.MULTILINE
            )
        else:
            # Append the new section to the end of the file
            updated_content = content + f'\n{new_section}'

        # Write the updated content back to the file if there's a difference
        if config_file_content != updated_content:
            print(f"\nUpdating {section} section in Grafana configuration file...")
            with open(file, "w", encoding="utf-8") as config_file:
                config_file.write(updated_content)
            print(f"Successfully updated {section} section in Grafana configuration file.")
            return True
        else:
            print(f"[{section}] section in Grafana configuration file is already configured.")
            return False

    @classmethod
    def update_configuration(cls, is_deployment):
        print("\nChanging Grafana configuration file ownership...")
        if not Utils.has_terminal_output(["sudo", "chown", "-R", f"{Utils.os_username()}:root", Grafana.CONFIGURATION_DIRECTORY]):
            print("Unable to change Grafana configuration file ownership.")
        else:
            print("Successfully changed Grafana configuration file ownership.")

            was_updated = False
            for config_section in Grafana.CONFIGURATION_SECTIONS:
                was_updated = Grafana.update_section(Grafana.CONFIGURATION_FILE, config_section["section"], config_section["content"])

            if was_updated:
                Grafana.restart()

            if is_deployment:
                Grafana.restart()

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
