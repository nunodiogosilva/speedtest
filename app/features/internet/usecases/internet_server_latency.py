import time
from speedtest import SpeedtestException
from app.config.gauges import Gauges


class InternetServerLatency:

    def __init__(self, speedtest, network_name):
        self.server = self.get_internet_server_latency(speedtest, network_name)

    def get_internet_server_latency(self, speedtest, network_name):
        print("Finding best internet server...")
        internet_server = None

        while internet_server is None:
            try:
                best_internet_server = speedtest.get_best_server()
                latency = best_internet_server["latency"]
                internet_server = f"({best_internet_server['sponsor']}) " \
                    f"{best_internet_server['name']}, " \
                    f"{best_internet_server['country']} " \
                    f"({best_internet_server['cc']})"
                print(f"Best internet server: {internet_server}")

                Gauges.INTERNET_SERVER_LATENCY_GAUGE.labels(
                    network_name=network_name,
                    internet_server=internet_server
                ).set(latency)

            except SpeedtestException as error:
                print(error)
                print("Retrying in 1 second...")
                time.sleep(1)

        return internet_server
