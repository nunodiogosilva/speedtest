from prometheus_client import Gauge


class Gauges:

    INTERNET_SERVER_LATENCY_GAUGE = Gauge(
        'internet_server_latency',
        'Internet server latency in seconds',
        [
            'network_name',
            'internet_server'
        ]
    )

    INTERNET_DOWNLOAD_SPEED_GAUGE = Gauge(
        'internet_download_speed',
        'Internet download speed in Mbps',
        [
            'network_name',
            'internet_server'
        ]
    )

    INTERNET_UPLOAD_SPEED_GAUGE = Gauge(
        'internet_upload_speed',
        'Internet upload speed in Mbps',
        [
            'network_name',
            'internet_server'
        ]
    )
