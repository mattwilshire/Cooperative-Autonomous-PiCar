from flask import Flask, render_template, jsonify
from threading import Thread, Event
from time import sleep
import socket

app = Flask(__name__)

started = False

thread = None
thread_interrupt = Event()

packets = []

def send(message):
    UDP_IP = "192.168.4.255"
    UDP_PORT = 5000
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.sendto(message.encode(), (UDP_IP, UDP_PORT))

def start_thread():
    global thread
    global thread_interrupt
    global packets
    send("start")
    thread = Thread(target=listen, args=(thread_interrupt, packets))
    thread.start()

def stop_thread():
    global thread_interrupt
    global thread
    thread_interrupt.set()
    thread.join()
    send("kill")

def listen(thread_interrupt, packets):
    localIP     = ""
    localPort   = 5000
    bufferSize  = 1024

    server_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    server_socket.bind((localIP, localPort))

    while True:
        if thread_interrupt.is_set():
            break

        bytesAddressPair = server_socket.recvfrom(bufferSize)
        message = bytesAddressPair[0]
        message = message.decode()

        try:
            message = json.loads(message)
            packets.append(message)
        except:
            pass

@app.route('/start', methods=['GET'])
def start():
    global started
    if started:
        return "NO"
    started = True
    start_thread()
    return "OK"

@app.route('/stop', methods=['GET'])
def stop():
    global started
    if started:
        started = False
        stop_thread()
        return "OK"
    return "NO"

@app.route('/poll', methods=['GET'])
def poll():
    global packets
    return jsonify(packets)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)