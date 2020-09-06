import socket
import urllib.request
import ipaddress
from threading import Thread
import time

class IPAddressProperty:

    def __init__(self, logger, thing):
        self.logger = logger
        self.thing = thing

        self.ip_address = self.thing.find_or_create_property('IP Address', 'IP_ADDRESS')
        
        self.thread_ip_address = Thread(target=self.update)
        self.thread_ip_address.start()

    def update(self):
        local_ip = get_local_ip()
        type_local_ip = check_type_ip(local_ip)
        external_ip = get_external_ip()
        type_external_ip = check_type_ip(external_ip)
        values = (local_ip, type_local_ip, external_ip, type_external_ip)
        self.ip_address.update_values(values)
        # Wait for 5 minutes
        time.sleep(300)
        # then check the ip address again
        self.update()


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def get_external_ip():
    return urllib.request.urlopen('https://ident.me').read().decode('utf8')

def check_type_ip(ip_str):
    ip = ipaddress.ip_address(ip_str)
    return ip.version
