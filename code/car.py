import picar
import cv2
import datetime
from hand_coded_lane_follower import HandCodedLaneFollower
from threading import Thread
import json

class PiCar(object):
    __INITIAL_SPEED = 0
    __SCREEN_WIDTH = 320
    __SCREEN_HEIGHT = 240

    def __init__(self, event):
        """ Init camera and wheels"""
        self.event = event

        self.sent_request = False
        self.reached_merge = False
        picar.setup()

        self.camera = cv2.VideoCapture(-1)
        self.camera.set(3, self.__SCREEN_WIDTH)
        self.camera.set(4, self.__SCREEN_HEIGHT)

        f = open('config.json')
        self.car_data = json.load(f)

        self.id = self.car_data["id"]

        if "pitch" in self.car_data["camera"]:
            self.pan_servo = picar.Servo.Servo(1)
            self.pan_servo.offset = self.car_data['camera']['pitch']  # calibrate servo to center
            self.pan_servo.write(90)

        if "yaw" in self.car_data["camera"]:
            self.tilt_servo = picar.Servo.Servo(2)
            self.tilt_servo.offset = self.car_data['camera']['yaw'] # calibrate servo to center
            self.tilt_servo.write(90)

        # Back wheels
        self.back_wheels = picar.back_wheels.Back_Wheels()
        self.back_wheels.speed = 0

        # Front wheels
        self.front_wheels = picar.front_wheels.Front_Wheels()
        self.front_wheels.turning_offset = self.car_data['camera']['steering']  # calibrate servo to center
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
        cv2.destroyAllWindows()

    def drive(self, speed=__INITIAL_SPEED):
        """ Main entry point of the car, and put it in drive mode

        Keyword arguments:
        speed -- speed of back wheel, range is 0 (stop) - 100 (fastest)
        """

        #logging.info('Starting to drive at speed %s...' % speed)
        self.back_wheels.speed = speed
        while self.camera.isOpened():
            if self.event.is_set():
                self.cleanup()
                break

            _, image_lane = self.camera.read()
            if self.car_data['id'] == 1 :
                image_lane = self.follow_lane(image_lane)

            

    def follow_lane(self, image):
        image = self.lane_follower.follow_lane(image)
        return image