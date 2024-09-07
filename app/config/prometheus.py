import os
from dotenv import load_dotenv
from prometheus_client import start_http_server
from app.common.utils import Utils
from app.config.paths import Paths


class Prometheus:

    def __init__(self):
        load_dotenv()
        self.hostname = Utils.os_hostname()
        self.service_name = "prometheus"
        self.service_description = "Prometheus"
        self.port = os.getenv("PROMETHEUS_PORT")
        self.node_port = os.getenv("PROMETHEUS_NODE_PORT")
        self.metrics_port = os.getenv("PROMETHEUS_METRICS_PORT")
        self.alertmanager_port = os.getenv("PROMETHEUS_ALERTMANAGER_PORT")
        self.config = os.getenv("PROMETHEUS_CONFIG_PATH")
        self.templates = f"{Paths.TEMPLATES_DIRECTORY}/prometheus"
        self.config_template = f"{self.templates}/prometheus.yml"

    def setup(self, is_deployment=False):
        Utils.create_file(self.config)
        config_content = Utils.get_file_content(self.config)
        config_template_content = Utils.get_file_content(self.config_template)
        self.update_alertmanager_targets(config_template_content["alerting"]["alertmanagers"])
        self.update_jobs_targets(config_template_content["scrape_configs"])
        if config_content == config_template_content:
            print("Prometheus is already configured.")

            if is_deployment:
                Utils.restart_service(self.service_name, self.service_description)
        else:
            print("Updating Prometheus configuration file...")
            Utils.update_file(self.config, config_template_content, "w")
            print("Successfully updated Prometheus configuration file.")

            if is_deployment:
                Utils.restart_service(self.service_name, self.service_description)
            else:
                Utils.reload_service(self.service_name, self.service_description)

    def update_alertmanager_targets(self, alertmanager):
        alertmanager[0]["static_configs"][0]["targets"] = [
            f"{self.hostname}:{self.alertmanager_port}"
        ]

    def update_jobs_targets(self, scrape_configs):
        for scrape_config in scrape_configs:
            if scrape_config["job_name"] == "prometheus":
                scrape_config["static_configs"][0]["targets"] = [
                    f"{self.hostname}:{self.port}"
                ]
            elif scrape_config["job_name"] == "node":
                scrape_config["static_configs"][0]["targets"] = [
                    f"{self.hostname}:{self.node_port}"
                ]
            elif scrape_config["job_name"] == "metrics":
                scrape_config["static_configs"][0]["targets"] = [
                    f"{self.hostname}:{self.metrics_port}"
                ]

    def start_server(self):
        start_http_server(self.metrics_port)
