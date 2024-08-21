from app.common.utils import Utils
from app.config.paths import Paths


class Python:

    VERSION = "python3.11"

    PIP_VERSION = "pip3.11"

    INTERPRETER_FILE = f"/usr/bin/{VERSION}"

    PIP_REQUIREMENTS_FILE = f"{Paths.PROJECT_DIRECTORY}/requirements.txt"

    @classmethod
    def setup(cls):
        if not Utils.has_terminal_output(["sudo", Python.VERSION, "--version"]):
            print("Updating packages...")
            if not Utils.has_terminal_input(["sudo", "apt-get", "update"]):
                print("Unable to update packages.")
            else:
                print(f"Installing Python {Python.VERSION} version...")
                if not Utils.has_terminal_input(["sudo", "apt-get", "install", Python.VERSION]):
                    print(
                        f"Unable to install Python {Python.VERSION} version.")
                else:
                    print(
                        f"Successfully installed Python {Python.VERSION} version.")

        Python.setup_pip()

    @classmethod
    def setup_pip(cls):
        print("Creating a Python virtual environment...")
        if not Utils.has_terminal_output(["sudo", Python.VERSION, "-m", "venv", f"{Paths.PROJECT_DIRECTORY}/.venv"]):
            print("Unable to create a Python virtual environment.")
        else:
            print("Activating Python virtual environemnt...")
            if not Utils.has_terminal_output(["source", f"{Paths.PROJECT_DIRECTORY}/.venv/bin/activate"]):
                print("Unable to activate Python virtual environment.")
            else:
                requirements = []
                with open(Python.PIP_REQUIREMENTS_FILE, "r", encoding="utf-8") as file:
                    requirements = [line.split("==")[0]
                                    for line in file.readlines()]

                installed_packages = Utils.get_terminal_output(
                    [Python.PIP_VERSION, "freeze"]
                ).splitlines()

                missing_packages = [
                    requirement for requirement in requirements if requirement not in installed_packages]

                if not missing_packages:
                    print("Required Python packages are already installed.")
                else:
                    print("Installing required Python packages...")
                    if not Utils.has_terminal_input([Python.PIP_VERSION, "install", "-r", Python.PIP_REQUIREMENTS_FILE]):
                        print("Unable to install required Python packages.")
                    else:
                        print("Successfully installed required Python packages.")
