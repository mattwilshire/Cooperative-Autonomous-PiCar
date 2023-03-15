from environment import Environment
import socket
import threading
import json

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
    try:
        message = json.loads(message)
        is_json = True
    except ValueError:
        pass

    if is_json:
        environment_thread.on_network_message(message)
    else:
        if message == "start":
            print("Starting Environment!")
            environment_thread_interrupt = threading.Event()
            environment_thread = Environment(environment_thread_interrupt)
            environment_thread.daemon = True
            environment_thread.start()
        elif message == "kill":
            environment_thread_interrupt.set()
            print("Killing start thread!")
        elif message == "quit":
            print("Received quit from network!")
            environment_thread_interrupt.set()
            exit()