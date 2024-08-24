import time
from speedtest import SpeedtestException
from app.config.gauges import Gauges


class InternetServerLatency:

    def __init__(self, speedtest, network):
        self.server = self.get_internet_server_latency(speedtest, network)

    def get_internet_server_latency(self, speedtest, network):
        print("Finding best internet server...")
        server = None

        while server is None:
            try:
                best_server = speedtest.get_best_server()
                latency = best_server["latency"]
                server = f"({best_server['sponsor']}) " \
                    f"{best_server['name']}, " \
                    f"{best_server['country']} " \
                    f"({best_server['cc']})"
                print(f"Best internet server: {server}")

                Gauges.INTERNET_SERVER_LATENCY_GAUGE.labels(
                    network=network,
                    server=server
                ).set(latency)

            except SpeedtestException as error:
                print(error)
                print("Retrying in 1 second...")
                time.sleep(1)

        return server
