from threading import Thread, Event
from car import PiCar
from gps import GPS
import json
import time
import socket
import math

class Environment(Thread):

	def __init__(self, event, ip_address):
		Thread.__init__(self)
		
		self.event = event
		self.ip = ip_address
		self.car_speeds = 50

		f = open('config.json')
		self.car_data = json.load(f)[ip_address]

		''' Network settings for sending broadcasting information '''
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
		self.UDP_IP = "192.168.4.255"
		self.UDP_PORT = 5000

	def run(self):
		self.gps_thread_interrupt = Event()
		with PiCar(self, self.event, self.car_data, self.ip) as car:
			self.car = car
			self.car.id = self.ip[-1]

			self.gps = GPS(self, self.on_gps_update, self.gps_thread_interrupt, self.car_data)
			self.gps.daemon = True
			self.gps.start()
			self.car.gps_thread_interrupt = self.gps_thread_interrupt
			
			car.drive(self.car_speeds)

	def on_gps_update(self, coords):
		x = coords[0]
		y = coords[1]

		if self.car.id == "1" and not self.car.sent_request:
			dist = math.sqrt((self.gps.route['merge_x'] - x) ** 2 + (self.gps.route['merge_y'] - y) ** 2)
			print("DISTANCE", dist)
			if dist <= 160:
				to_pos = [self.gps.route['merge_x'], self.gps.route['merge_y']]
				curr_pos = [coords[0], coords[1]]
				self.car.send_request(dist, to_pos, curr_pos)

		if self.car.id == "1" and y >= self.car_data['route']['merge_y'] - 60 and not self.car.reached_merge:
			current_time = int(time.time())
			msg_json = {}
			msg_json['TYPE'] = 'FINISH'
			msg_json['CURRENT_TIME'] = current_time
			msg_json['SOURCE'] = self.car.id
			msg_json['X'] = coords[0]
			msg_json['Y'] = coords[1]
			msg_json = json.dumps(msg_json)
			self.sock.sendto(msg_json.encode(), (self.UDP_IP, self.UDP_PORT))

		if y >= self.car_data['route']['dest_y']:
			self.event.set()

	def on_network_message(self, message):
		''' We got a message from ourselves on the broadcast, discard it.'''
		if message['SOURCE'] == self.car.id:
			return

		current_time = int(time.time())

		if message['TYPE'] == 'REQUEST':
			their_eta = float(message['ETA'])
			dist = math.sqrt((self.gps.route['merge_x'] - self.gps.x) ** 2 + (self.gps.route['merge_y'] - self.gps.y) ** 2)
			eta = current_time + dist / self.car_speeds
			if (eta - their_eta) < 3:
				eta += 3

			msg_json = {
				'TYPE' : 'CONFIRM',
				'CURRENT_TIME' : current_time,
				'DISTANCE' : dist,
				'SOURCE' : self.car.id,
				'RESPONDING_TO' : message['SOURCE'],
				'POSITION' : [self.gps.x, self.gps.y],
				'ETA' : dist / self.car_speeds,
				'ETA_TIME' : eta
			}

			self.car.broadcast(msg_json)
		elif message['TYPE'] == 'CONFIRM':
			msg_json = {
				'TYPE' : 'GLOBAL',
				'SOURCE' : self.car.id
			}
			msg_json['PLAN'] = {}
			msg_json['PLAN'][message['SOURCE']] = message

			self.car.broadcast(msg_json)
		elif message['TYPE'] == 'GLOBAL':
			if str(self.car.id) in message['PLAN']:
				eta = float(message['PLAN'][str(self.car.id)]['ETA_TIME'])
				dist = math.sqrt((self.gps.route['merge_x'] - self.gps.x) ** 2 + (self.gps.route['merge_y'] - self.gps.y) ** 2)
				speed = (eta - current_time) * 3
				self.car.back_wheels.speed = speed
				print(f"--------------------Adjusted speed to {speed}")
		elif message['TYPE'] == 'FINISH':
			self.car.back_wheels.speed = self.car_speeds



