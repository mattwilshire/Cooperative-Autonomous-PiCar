import socket
import json

UDP_IP = "192.168.4.255"
UDP_PORT = 5000

while True:
	command = input("Send to network: ")
	if command == "json":
		m_json = {}
		m_json['type'] = 'HELLO' 
		m_json['data'] = 240 
		command = json.dumps(m_json)

	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
	sock.sendto(command.encode(), (UDP_IP, UDP_PORT))

