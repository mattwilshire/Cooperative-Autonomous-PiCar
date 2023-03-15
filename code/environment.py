from threading import Thread, Event
from car import PiCar
from gps import GPS
import json
import time
import socket
import math

UDP_IP = "192.168.4.255"
UDP_PORT = 5000

class Environment(Thread):

	def __init__(self, event):
		Thread.__init__(self)
		self.event = event
		f = open('config.json')
		self.car_data = json.load(f)
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

	def run(self):
		speed = 40
		self.gps_thread_interrupt = Event()
		with PiCar(self.event) as car:
			self.car = car
			self.car.id = self.car_data['id']

			self.gps = GPS(speed, self.on_gps_update, self.gps_thread_interrupt)
			self.gps.daemon = True
			self.gps.start()
			self.car.gps_thread_interrupt = self.gps_thread_interrupt
			
			car.drive(speed)

	def on_gps_update(self, coords):
		x = coords[0]
		y = coords[1]

		if self.car.id == 1 and not self.car.sent_request:
			dist = math.sqrt((self.gps.route['merge_x'] - x) ** 2 + (self.gps.route['merge_y'] - y) ** 2)
			if dist <= 160:
				current_time = int(time.time())
				msg_json = {}
				msg_json['TYPE'] = 'REQUEST'
				msg_json['CURRENT_TIME'] = current_time
				msg_json['SOURCE'] = self.car.id
				msg_json['DISTANCE'] = dist
				msg_json['X'] = coords[0]
				msg_json['Y'] = coords[1]
				msg_json['ETA'] = current_time + (dist / 40)
				msg_json = json.dumps(msg_json)
				self.sock.sendto(msg_json.encode(), (UDP_IP, UDP_PORT))
				self.car.sent_request = True

		if self.car.id == 1 and y >= self.car_data['route']['merge_y'] - 60 and not self.car.reached_merge:
			current_time = int(time.time())
			msg_json = {}
			msg_json['TYPE'] = 'FINISH'
			msg_json['CURRENT_TIME'] = current_time
			msg_json['SOURCE'] = self.car.id
			msg_json['X'] = coords[0]
			msg_json['Y'] = coords[1]
			msg_json = json.dumps(msg_json)
			self.sock.sendto(msg_json.encode(), (UDP_IP, UDP_PORT))

		if y >= self.car_data['route']['dest_y']:
			self.event.set()

	def on_network_message(self, message):
		if message['SOURCE'] == self.car.id:
			return

		if message['TYPE'] == 'REQUEST':
			current_time = int(time.time())
			their_eta = float(message['ETA'])
			dist = math.sqrt((self.gps.route['merge_x'] - self.gps.x) ** 2 + (self.gps.route['merge_y'] - self.gps.y) ** 2)
			eta = current_time + dist / 40
			if (eta - their_eta) < 3:
				eta += 3

			msg_json = {}
			msg_json['TYPE'] = 'CONFIRM'
			msg_json['CURRENT_TIME'] = current_time
			msg_json['DISTANCE'] = dist
			msg_json['SOURCE'] = self.car.id
			msg_json['RESPONDING_TO'] = message['SOURCE']
			msg_json['X'] = self.gps.x
			msg_json['Y'] = self.gps.y
			msg_json['ETA'] = dist / 40
			msg_json['ETA_TIME'] = eta
			msg_json = json.dumps(msg_json)

			self.sock.sendto(msg_json.encode(), (UDP_IP, UDP_PORT))
		elif message['TYPE'] == 'CONFIRM':
			msg_json = {}
			msg_json['TYPE'] = 'GLOBAL'
			msg_json['SOURCE'] = self.car.id
			msg_json['PLAN'] = {}
			msg_json['PLAN'][message['SOURCE']] = message
			msg_json = json.dumps(msg_json)
			self.sock.sendto(msg_json.encode(), (UDP_IP, UDP_PORT))
		elif message['TYPE'] == 'GLOBAL':
			if str(self.car.id) in message['PLAN']:
				current_time = int(time.time())
				eta = float(message['PLAN'][str(self.car.id)]['ETA_TIME'])
				dist = math.sqrt((self.gps.route['merge_x'] - self.gps.x) ** 2 + (self.gps.route['merge_y'] - self.gps.y) ** 2)
				speed = (eta - current_time) * 3
				self.car.back_wheels.speed = speed
				print(f"--------------------Adjusted speed to {speed}")
		elif message['TYPE'] == 'FINISH':
			self.car.back_wheels.speed = 40



