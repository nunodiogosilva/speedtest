import os
import subprocess


class Utils:

    @staticmethod
    def username():
        return os.getlogin()

    @staticmethod
    def create_file(file, content="", permission=None):
        if not os.path.exists(file):
            with open(file, "w", encoding="utf-8") as created_file:
                created_file.write(content)

            if permission:
                os.chmod(file, int(f"0o{permission}", 8))

    @staticmethod
    def update_file(file, content, update_type, permission=None):
        with open(file, update_type, encoding="utf-8") as updated_file:
            updated_file.write(content)

        if permission:
            os.chmod(file, int(f"0o{permission}", 8))

    @staticmethod
    def has_terminal_output(command: list):
        try:
            subprocess.check_output(command)
            return True

        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    @staticmethod
    def get_terminal_output(command: list):
        try:
            return subprocess.check_output(command, text=True)

        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    @staticmethod
    def has_terminal_input(command: list):
        try:
            subprocess.check_call(command)
            return True

        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
