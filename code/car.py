import picar
import cv2
import datetime
from hand_coded_lane_follower import HandCodedLaneFollower
from threading import Thread
import json
import time

UDP_IP = "192.168.4.255"
UDP_PORT = 5000

class PiCar(object):
    __INITIAL_SPEED = 0
    __SCREEN_WIDTH = 320
    __SCREEN_HEIGHT = 240


    def __init__(self, environment, event, car_data, ip):
        """ Init camera and wheels"""
        self.environment = environment
        self.event = event
        self.car_data = car_data
        self.ip = ip
        self.id = self.ip[-1]
       
        self.sent_request = False
        self.reached_merge = False

        ''' Camera Setup '''
        picar.setup()
        self.camera = cv2.VideoCapture(-1)
        self.camera.set(3, self.__SCREEN_WIDTH)
        self.camera.set(4, self.__SCREEN_HEIGHT)

        #self.video = cv2.VideoWriter('video.mp4', cv2.VideoWriter_fourcc(*'DIVX'), 20.0, (self.__SCREEN_WIDTH, self.__SCREEN_HEIGHT))

        if "pitch" in self.car_data["config"]:
            self.pan_servo = picar.Servo.Servo(1)
            self.pan_servo.offset = self.car_data['config']['pitch'] 
            self.pan_servo.write(90)

        if "yaw" in self.car_data["config"]:
            self.tilt_servo = picar.Servo.Servo(2)
            self.tilt_servo.offset = self.car_data['config']['yaw']
            self.tilt_servo.write(90)

        # Back wheels
        self.back_wheels = picar.back_wheels.Back_Wheels()
        self.back_wheels.speed = 0

        # Front wheels
        self.front_wheels = picar.front_wheels.Front_Wheels()
        self.front_wheels.turning_offset = self.car_data['config']['steering'] 
        self.front_wheels.turn(90)  # Steering Range is 45 (left) - 90 (center) - 135 (right)

        self.lane_follower = HandCodedLaneFollower(self)

    def __enter__(self):
        """ Entering a with statement """
        return self

    def __exit__(self, _type, value, traceback):
        """ Exit a with statement"""
        if traceback is not None:
            pass
        self.cleanup()

    def cleanup(self):
        """ Reset the hardware"""
        self.gps_thread_interrupt.set()
        self.back_wheels.speed = 0
        self.front_wheels.turn(90)
        self.camera.release()
        #self.video.release()
        cv2.destroyAllWindows()

    def drive(self, speed=__INITIAL_SPEED):
        """ Main entry point of the car, and put it in drive mode

        Keyword arguments:
        speed -- speed of back wheel, range is 0 (stop) - 100 (fastest)
        """
        self.back_wheels.speed = speed
        while self.camera.isOpened():
            if self.event.is_set():
                self.cleanup()
                break

            _, image_lane = self.camera.read()
            #self.video.write(image_lane)
            if (self.id == "1" and self.environment.switch == False) or (self.id == "2" and self.environment.switch == True):
                image_lane = self.follow_lane(image_lane)
                

    def follow_lane(self, image):
        image = self.lane_follower.follow_lane(image)
        return image

    def send_request(self, distance, to_pos, curr_pos):
        current_time = int(time.time())
        msg_json = {
            'TYPE' : 'REQUEST',
            'CURRENT_TIME' : current_time,
            'SOURCE' : self.id,
            'DISTANCE': distance,
            'POSITION': curr_pos,
            'TO_POSITION' : to_pos,
            'ETA' : current_time + (distance / self.environment.car_speeds)
        }
        print(msg_json)
        self.broadcast(msg_json)
        self.sent_request = True
    
    def broadcast(self, message):
        msg_json = json.dumps(message)
        self.environment.sock.sendto(msg_json.encode(), (self.environment.UDP_IP, self.environment.UDP_PORT))
