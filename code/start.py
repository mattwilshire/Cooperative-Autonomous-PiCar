from environment import Environment
from iputils import get_ip, is_allowed_ip
import socket
import threading
import json

ip_address = get_ip()
if not is_allowed_ip(ip_address):
    print('IP is not allowed must be either 192.168.4.1 or 192.168.4.2')
    exit()

'''
    Server Setup
    Listens to every message on the broadcast address (192.168.4.255)
'''

localIP     = ""
localPort   = 5000
bufferSize  = 1024

server_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
server_socket.bind((localIP, localPort))

environment_thread_interrupt = None
environment_thread = None

while True:
    print("Waiting for command from network !")
    is_json = False
    
    bytesAddressPair = server_socket.recvfrom(bufferSize)
    message = bytesAddressPair[0]
    address = bytesAddressPair[1]
    message = message.decode()
    args = None

    try:
        message = json.loads(message)
        is_json = True
    except ValueError:
        args = message.split(' ')[1:]
        message = message.split(' ')[0]

    if is_json:
        environment_thread.on_network_message(message)
    else:
        if message == "start":
            environment_thread_interrupt = threading.Event()
            collide = False
            loss_amount = 0
            print("Starting the environment!")
            if len(args) > 0:
                if args[0] == 'collide':
                    print("Collision is on!!!")
                    collide = True
                elif args[0] == 'loss':
                    loss_amount = args[1]
            environment_thread = Environment(environment_thread_interrupt, ip_address, collide, loss_amount)
            environment_thread.daemon = True
            environment_thread.start()
        elif message == "switch":
            environment_thread_interrupt = threading.Event()
            environment_thread = Environment(environment_thread_interrupt, ip_address, False, switch=True)
            environment_thread.daemon = True
            environment_thread.start()
        elif message == "kill":
            environment_thread_interrupt.set()
            print("Killing start thread!")
        elif message == "quit":
            print("Received quit from network!")
            environment_thread_interrupt.set()
            exit()