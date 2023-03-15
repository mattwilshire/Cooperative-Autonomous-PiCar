from threading import Thread
import time
import math
import json

class GPS(Thread):

	def __init__(self, speed, callback, event):
		Thread.__init__(self)

		f = open('config.json')
		car_data = json.load(f)
		self.route = car_data['route']
		self.x = self.route['x']
		self.y = self.route['y']
		self.merge_x = self.route['merge_x']
		self.merge_y = self.route['merge_y']

		self.speed = speed
		self.callback = callback
		self.event = event

	def run(self):
		while True:
			time.sleep(1)
			if self.event.is_set():
				break

			angle = math.atan2(self.merge_y - self.y, self.merge_x - self.x)
			dx = self.speed * math.cos(angle)
			dy = self.speed * math.sin(angle)

			self.x += dx
			self.y += dy

			self.callback([self.x, self.y])