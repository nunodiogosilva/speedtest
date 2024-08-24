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

    CONFIGURATION = [
        {
            "section": "[auth.anonymous]",
            "config": {
                "enabled": "true",
                "org_name": "Main Org.",
                "org_role": "Viewer",
                "hide_version": "true",
                "device_limit": "3"
            }
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
    def update_configuration(cls, is_deployment):
        print("\nChanging Grafana configuration file ownership...")
        if not Utils.has_terminal_output(["sudo", "chown", "-R", f"{Utils.os_username()}:root", Grafana.CONFIGURATION_DIRECTORY]):
            print("Unable to change Grafana configuration file ownership.")
        else:
            print("Successfully changed Grafana configuration file ownership.")
            with open(Grafana.CONFIGURATION_FILE, "r", encoding="utf-8") as file:
                lines = file.readlines()

            updated_lines = []
            sections = set()
            section_updated = False

            section = None
            in_section = False

            for line in lines:
                stripped_line = line.strip()

                # Check if the line indicates a section header
                if stripped_line.startswith("[") and stripped_line.endswith("]"):
                    if in_section:
                        # Process the section if we were previously in one
                        if section == config['section']:
                            # Check if there were any changes in the section
                            if section_updated:
                                # Add the updated section to the lines
                                updated_lines.append(f"\n{section}\n")
                                for key, value in config['config'].items():
                                    updated_lines.append(
                                        f"{key} = {value}\n")
                            else:
                                # Add the original section
                                updated_lines.append(line)

                    # Update the current section
                    section = stripped_line
                    in_section = False
                    updated_lines.append(line)
                    continue

                # Check if we're in a section that needs updating
                for config in Grafana.CONFIGURATION:
                    if section == config['section']:
                        in_section = True
                        sections.add(section)
                        keys_to_update = config['config']

                        # Flag to check if any value has changed
                        section_updated = False

                        # Process key-value pairs within the section
                        for key, value in keys_to_update.items():
                            if stripped_line.startswith(key):
                                # Compare existing value with the new value
                                if stripped_line != f"{key} = {value}":
                                    updated_lines.append(
                                        f"{key} = {value}\n")
                                    section_updated = True
                                break
                        else:
                            updated_lines.append(line)
                        break
                else:
                    # If not in a section that needs updating, just append the line
                    if not in_section:
                        updated_lines.append(line)

            # Add any missing sections and key-value pairs
            for config in Grafana.CONFIGURATION:
                if config['section'] not in sections:
                    updated_lines.append(f"\n{config['section']}\n")
                    for key, value in config['config'].items():
                        updated_lines.append(f"{key} = {value}\n")

            # Write the updated lines back to the file if there were changes
            if updated_lines != lines:
                print("\nUpdating Grafana configuration file...")
                with open(Grafana.CONFIGURATION_FILE, 'w', encoding="utf-8") as file:
                    file.writelines(updated_lines)
                print("Successfully updated Grafana configuration file.")
                Grafana.restart()

            else:
                print("\nGrafana is already configured.")

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
