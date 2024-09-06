import os
from dotenv import load_dotenv
from prometheus_client import start_http_server
from app.common.utils import Utils
from app.config.paths import Paths


class Prometheus:

    def __init__(self):
        load_dotenv()
        self.service_name = "prometheus"
        self.service_description = "Prometheus"
        self.metrics_port = os.getenv("PROMETHEUS_METRICS_PORT")
        self.config = os.getenv("PROMETHEUS_CONFIG_PATH")
        self.templates = f"{Paths.TEMPLATES_DIRECTORY}/prometheus"
        self.config_template = f"{self.templates}/prometheus.yml"

    def setup(self, is_deployment=False):
        Utils.create_file(self.config)
        config_content = Utils.get_file_content(self.config)
        config_template_content = Utils.get_file_content(self.config_template)
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

    def start_server(self):
        start_http_server(self.metrics_port)
