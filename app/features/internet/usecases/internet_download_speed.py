import time
from speedtest import SpeedtestException
from app.config.gauges import Gauges


class InternetDownloadSpeed:

    def __init__(self, speedtest, network, server):
        self.get_internet_download_speed(speedtest, network, server)

    def get_internet_download_speed(self, speedtest, network, server):
        print("Measuring internet download speed...")
        internet_download_speed = None

        while internet_download_speed is None:
            try:
                internet_download_speed = speedtest.download() / \
                    1_000_000  # Convert to Mbps
                print(
                    f"Internet Download Speed: {internet_download_speed:.2f} Mbps")

                Gauges.INTERNET_DOWNLOAD_SPEED_GAUGE.labels(
                    network=network,
                    server=server
                ).set(internet_download_speed)

            except SpeedtestException as error:
                print(error)
                print("Retrying in 1 second...")
                time.sleep(1)
