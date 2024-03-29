from threading import Thread, Event
from car import PiCar
from gps import GPS
import json
import time
import socket
import math
import random
#TEST
class Environment(Thread):

	def __init__(self, event, ip_address, collide, switch=False, loss_amount=0):
		Thread.__init__(self)
		
		self.event = event
		self.ip = ip_address
		self.switch = switch

		self.loss = loss_amount

		if switch == True:
			if self.ip[-1] == "1":
				self.ip = "192.168.4.2"
			else:
				self.ip = "192.168.4.1"
		
		self.car_speeds = 50
		self.collide = collide

		f = open('config.json')
		data = json.load(f)
		self.car_data = data[self.ip]

		if switch:
			self.car_data['config'] = data[ip_address]['config']

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
			self.car.sent_finish = False
			print(self.ip)

			self.gps = GPS(self, self.on_gps_update, self.gps_thread_interrupt, self.car_data)
			self.gps.daemon = True
			self.gps.start()
			self.car.gps_thread_interrupt = self.gps_thread_interrupt
			
			car.drive(self.car_speeds)

	def on_gps_update(self, coords):
		x = coords[0]
		y = coords[1]
		current_time = int(time.time())

		if self.car.id == "1" and not self.car.sent_request and not self.collide:
			dist = math.sqrt((self.gps.route['merge_x'] - x) ** 2 + (self.gps.route['merge_y'] - y) ** 2)
			if dist <= 80:
				to_pos = [self.gps.route['merge_x'], self.gps.route['merge_y']]
				self.car.send_request(dist, to_pos, coords)

		if self.car.id == "1" and y >= self.car_data['route']['merge_y'] and not self.car.reached_merge and not self.car.sent_finish:
			msg_json = {
				'TYPE' : 'FINISH',
				'CURRENT_TIME' : current_time,
				'SOURCE' : self.car.id,
				'POSITION': coords
			}
			print(msg_json)
			self.car.broadcast(msg_json)
			self.car.sent_finish = True

		if y >= self.car_data['route']['dest_y']:
			self.event.set()

	def on_network_message(self, message):
		if "LOSS" in message:
			return
		
		''' We got a message from ourselves on the broadcast, discard it.'''
		if message['SOURCE'] == self.car.id:
			return
		random_val = random.random()

		if random_val < (self.loss / 100):
			print("LOST PACKET: %s" % message)
			message["LOSS"] = 1
			self.car.broadcast(message)
			return
		
		current_time = int(time.time())

		if message['TYPE'] == 'REQUEST':
			their_eta = float(message['ETA'])
			dist = math.sqrt((self.gps.route['merge_x'] - self.gps.x) ** 2 +
					 (self.gps.route['merge_y'] - self.gps.y) ** 2)
			eta = current_time + dist / self.car_speeds

			if (eta - their_eta) < 3:
				eta += 3

			msg_json = {
				'TYPE' : 'PROMISE',
				'CURRENT_TIME' : current_time,
				'DISTANCE' : dist,
				'SOURCE' : self.car.id,
				'RESPONDING_TO' : message['SOURCE'],
				'POSITION' : [self.gps.x, self.gps.y],
				'ETA' : dist / self.car_speeds,
				'ETA_TIME' : eta
			}

			self.car.broadcast(msg_json)
		elif message['TYPE'] == 'PROMISE':
			msg_json = {
				'TYPE' : 'CONFIRM',
				'SOURCE' : self.car.id
			}
			msg_json['PLAN'] = {}
			msg_json['PLAN'][message['SOURCE']] = message

			self.car.broadcast(msg_json)
		elif message['TYPE'] == 'CONFIRM':
			if str(self.car.id) in message['PLAN']:
				eta = float(message['PLAN'][str(self.car.id)]['ETA_TIME'])
				dist = math.sqrt((self.gps.route['merge_x'] - self.gps.x) ** 2 +
						 (self.gps.route['merge_y'] - self.gps.y) ** 2)
				speed = dist / (eta - current_time)
				self.car.back_wheels.speed = round(speed)
				print(f"Adjusted speed to {speed}")
				
				
				#speed = 20
		elif message['TYPE'] == 'FINISH':
			print("Received?")
			self.car.back_wheels.speed = self.car_speeds



