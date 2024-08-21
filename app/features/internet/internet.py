import time
from speedtest import Speedtest, SpeedtestException
from app.common.network import Network
from app.features.internet.usecases.internet_server_latency import InternetServerLatency
from app.features.internet.usecases.internet_download_speed import InternetDownloadSpeed
from app.features.internet.usecases.internet_upload_speed import InternetUploadSpeed


class Internet:

    def __init__(self):
        print("Connecting to Ookla Speedtest...")
        speedtest = None

        while speedtest is None:
            try:
                speedtest = Speedtest()
                network = Network()

                internet_server_latency = InternetServerLatency(
                    speedtest=speedtest,
                    network_name=network.name
                )

                InternetDownloadSpeed(
                    speedtest=speedtest,
                    network_name=network.name,
                    internet_server=internet_server_latency.server
                )
                InternetUploadSpeed(
                    speedtest=speedtest,
                    network_name=network.name,
                    internet_server=internet_server_latency.server
                )

            except SpeedtestException as error:
                print(error)
                print("Retrying in 1 second...")
                time.sleep(1)
