import eel
import time
from threading import Thread, Event
import socket
import json

started = False
thread = None
thread_interrupt = Event()

def send(message):
	UDP_IP = "192.168.4.255"
	UDP_PORT = 5000
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
	sock.sendto(message.encode(), (UDP_IP, UDP_PORT))

def listen(thread_interrupt):
	localIP     = ""
	localPort   = 5000
	bufferSize  = 1024

	server_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
	server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
	server_socket.bind((localIP, localPort))
	server_socket.settimeout(1)

	while True:
		if thread_interrupt.is_set():
			break
		try:
			bytesAddressPair = server_socket.recvfrom(bufferSize)
			message = bytesAddressPair[0]
			message = message.decode()
			try:
				message = json.loads(message)
				eel.receiveData(message)
			except:
				pass
		except:
			pass

@eel.expose
def start():
	global started
	if not started:
		global thread_interrupt
		global thread
		send("start")
		thread = Thread(target=listen, args=(thread_interrupt,) )
		thread.start()
		started = True

@eel.expose
def stop():
	global started
	print("WE SHOULD BE STOPPING!")
	if started:
		global thread_interrupt
		global thread
		thread_interrupt.set()
		thread.join()
		send("kill")
		started = False
		eel.fullyStopped()

eel.init("view")
eel.start('index.html', size=(1080, 900), position=(450,100))