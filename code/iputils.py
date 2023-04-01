import subprocess
import re

allowed_ips = ['192.168.4.1', '192.168.4.2']

def get_ip():
    ifconfig = subprocess.run(['ifconfig', 'wlan0'], stdout=subprocess.PIPE)
    ifconfig = ifconfig.stdout.decode()

    ip_address = re.search(r'(?<=inet\s)\S+', ifconfig).group(0)
    return ip_address

def is_allowed_ip(ip):
    if not ip in allowed_ips:
        return False
    return True