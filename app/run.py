from app.config.prometheus import Prometheus
from app.features.internet.internet import Internet


class App:

    def __init__(self):
        # Start Prometheus HTTP server
        Prometheus.start_server()

        # Periodically measure and update metrics
        while True:
            Internet()


if __name__ == "__main__":
    App()
