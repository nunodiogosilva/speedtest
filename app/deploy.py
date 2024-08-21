from app.config.prometheus import Prometheus
from app.config.grafana import Grafana
from app.config.service import Service


class Deploy:
    def __init__(self):
        Prometheus.setup(is_deployment=True)
        Grafana.setup(is_deployment=True)
        Service.setup(is_deployment=True)


if __name__ == "__main__":
    Deploy()
