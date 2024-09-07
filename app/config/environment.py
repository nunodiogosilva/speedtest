import os
import getpass
from dotenv import load_dotenv
from app.common.utils import Utils
from app.config.paths import Paths


class Environment:

    def __init__(self):
        self.variables = [
            {
                "key": "PROMETHEUS_CONFIG_PATH",
                "default": "/etc/prometheus/prometheus.yml",
                "hint": "(leave blank for default)"
            },
            {
                "key": "PROMETHEUS_PORT",
                "default": 9090,
                "hint": "(leave blank for default)"
            },
            {
                "key": "PROMETHEUS_URL",
                "default": "http://localhost:9090",
                "hint": "(leave blank for default)"
            },
            {
                "key": "PROMETHEUS_NODE_PORT",
                "default": 9100,
                "hint": "(leave blank for default)"
            },
            {
                "key": "PROMETHEUS_METRICS_PORT",
                "default": 8000,
                "hint": "(leave blank for default)"
            },
            {
                "key": "GRAFANA_CONFIG_PATH",
                "default": "/etc/grafana/grafana.ini",
                "hint": "(leave blank for default)"
            },
            {
                "key": "GRAFANA_PORT",
                "default": 3000,
                "hint": "(leave blank for default)"
            },
            {
                "key": "GRAFANA_URL",
                "default": "http://localhost:3000",
                "hint": "(leave blank for default)"
            },
            {
                "key": "GRAFANA_API_TOKEN",
                "hint": "(Get Service Account Token at http://localhost:3000/org/serviceaccounts)"
            },
            {
                "key": "SYSTEMD_CONFIG_PATH",
                "default": "/etc/systemd/system",
                "hint": "(leave blank for default)"
            }
        ]

    def setup(self):
        load_dotenv()
        print("Configuring Environment variables...")
        Utils.create_file(Paths.ENVIRONMENT_FILE)
        for variable in self.variables:
            if not os.getenv(variable["key"]):
                value = getpass.getpass(f"Enter {variable['key']} Environment variable value:\n>{variable['hint']} ").strip()
                if not value:
                    value = variable["default"] if variable["default"] else None
                    while value is None:
                        print(f"{variable['key']} Environment variable has no default value.")
                        value = getpass.getpass(f"Enter {variable['key']} Environment variable value:\n>{variable['hint']} ").strip()
                        if not value:
                            value = None
                content = f'{variable["key"]}="{value}"\n'
                Utils.update_file(Paths.ENVIRONMENT_FILE, content, "a")

            else:
                print(f"{variable['key']} Environment variable is already configured.")
