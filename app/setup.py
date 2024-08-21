from app.config.python import Python
from app.config.prometheus import Prometheus
from app.config.grafana import Grafana
from app.config.service import Service


class Setup:
    def __init__(self):
        Python.setup()
        Prometheus.setup()
        Grafana.setup()
        Service.setup()


if __name__ == "__main__":
    Setup()
