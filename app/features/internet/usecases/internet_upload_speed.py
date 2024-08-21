import time
from speedtest import SpeedtestException
from app.config.gauges import Gauges


class InternetUploadSpeed:

    def __init__(self, speedtest, network_name, internet_server):
        self.get_internet_upload_speed(speedtest, network_name, internet_server)

    def get_internet_upload_speed(self, speedtest, network_name, internet_server):
        print("Measuring internet upload speed...")
        internet_upload_speed = None

        while internet_upload_speed is None:
            try:
                internet_upload_speed = speedtest.upload() / 1_000_000  # Convert to Mbps
                print(
                    f"Internet Upload Speed: {internet_upload_speed:.2f} Mbps")

                Gauges.INTERNET_UPLOAD_SPEED_GAUGE.labels(
                    network_name=network_name,
                    internet_server=internet_server
                ).set(internet_upload_speed)

            except SpeedtestException as error:
                print(error)
                print("Retrying in 1 second...")
                time.sleep(1)
