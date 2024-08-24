import time
from speedtest import Speedtest, SpeedtestException
from app.common.utils import Utils
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
                network = Utils.os_network()

                server = InternetServerLatency(
                    speedtest=speedtest,
                    network=network
                ).server

                InternetDownloadSpeed(
                    speedtest=speedtest,
                    network=network,
                    server=server
                )

                InternetUploadSpeed(
                    speedtest=speedtest,
                    network=network,
                    server=server
                )

            except SpeedtestException as error:
                print(error)
                print("Retrying in 1 second...")
                time.sleep(1)
