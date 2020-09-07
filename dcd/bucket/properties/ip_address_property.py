import socket
import urllib.request
import ipaddress
from threading import Thread
import time
from ..thing_logger import ThingLogger
# from ..thing import Thing


IP_SCAN_FREQUENCY_SECONDS = 300

class IPAddressProperty:

    def __init__(self, logger: ThingLogger, thing):
        self.logger = logger
        self.thing = thing
        # Find or create the IP Address property
        self.ip_address = self.thing.find_or_create_property("IP Address", "IP_ADDRESS")
        # Run the recurring scan in a dedicated thread
        self.thread_ip_address = Thread(target=self.update)
        self.thread_ip_address.start()

    def update(self):
        local_ip = get_local_ip()
        type_local_ip = check_type_ip(local_ip)
        external_ip = get_external_ip()
        type_external_ip = check_type_ip(external_ip)
        values = (local_ip, type_local_ip, external_ip, type_external_ip)
        self.ip_address.update_values(values)
        # Wait till the next scan
        time.sleep(IP_SCAN_FREQUENCY_SECONDS)
        # then check the ip address again
        self.update()


def get_local_ip() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(("10.255.255.255", 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

def get_external_ip() -> str:
    return urllib.request.urlopen("https://ident.me").read().decode("utf8")

def check_type_ip(ip_str: str) -> int:
    ip = ipaddress.ip_address(ip_str)
    return ip.version
