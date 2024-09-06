import os
from dotenv import load_dotenv
from app.common.utils import Utils
from app.config.paths import Paths


class Service:

    def __init__(self):
        load_dotenv()
        self.name = "speedtest"
        self.description = "Speedtest Service"
        self.config = f"{os.getenv('SYSTEMD_CONFIG_PATH')}/{self.name}.service"
        self.templates = f"{Paths.TEMPLATES_DIRECTORY}/speedtest"
        self.config_template = f"{self.templates}/speedtest.service"
        self.config_template_args = {
            "description": self.description,
            "environment": Paths.ENVIRONMENT_FILE,
            "project": Paths.PROJECT_DIRECTORY,
            "bash_interpreter": Paths.BASH_INTERPRETER_FILE,
            "python_interpreter": Paths.PYTHON_INTERPRETER_FILE
        }

    def setup(self, is_deployment=False):
        Utils.create_file(self.config)
        config_content = Utils.get_file_content(self.config)
        config_template_content = Utils.get_template_content(
            self.templates,
            self.config_template,
            self.config_template_args
        )
        if config_content == config_template_content:
            print(f"{self.description} is already configured.")

            if is_deployment:
                Utils.restart_service(self.name, self.description)
        else:
            print(f"Updating {self.description} configuration file...")
            Utils.update_file(self.config, config_template_content, "w")
            print(
                f"Successfully updated {self.description} configuration file.")

            if is_deployment:
                Utils.restart_service(self.name, self.description)
            else:
                Utils.reload_service(self.name, self.description)
