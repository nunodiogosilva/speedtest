import os
import getpass
from dotenv import load_dotenv
from app.common.utils import Utils
from app.config.paths import Paths


class Environment:

    VARIABLES = [
        "OS_USERNAME",
        "GRAFANA_API_TOKEN"
    ]

    CONFIGURATION_FILE = f"{Paths.PROJECT_DIRECTORY}/.env"

    @classmethod
    def setup(cls):
        load_dotenv()
        print("\nConfiguring Environment variables...")
        Utils.create_file(Environment.CONFIGURATION_FILE)
        for variable in Environment.VARIABLES:
            if not os.getenv(variable):
                value = getpass.getpass(
                    f"Enter {variable} Environment variable value:\n> ")
                content = f'{variable}="{value}"\n'
                Utils.update_file(Environment.CONFIGURATION_FILE, content, "a")

            else:
                print(
                    f"{os.getenv(variable)} Environment variable already configured.")
