import logging
import picar
import cv2
import datetime
from hand_coded_lane_follower import HandCodedLaneFollower
from threading import Thread
import socket

_SHOW_IMAGE = True


class DeepPiCar(object):

    __INITIAL_SPEED = 0
    __SCREEN_WIDTH = 320
    __SCREEN_HEIGHT = 240

    def __init__(self):
        """ Init camera and wheels"""
        logging.info('Creating a DeepPiCar...')

        picar.setup()

        logging.debug('Set up camera')
        self.camera = cv2.VideoCapture(-1)
        self.camera.set(3, self.__SCREEN_WIDTH)
        self.camera.set(4, self.__SCREEN_HEIGHT)

        #self.pan_servo = picar.Servo.Servo(1)
        #self.pan_servo.offset = -10  # calibrate servo to center
        #self.pan_servo.write(90)

        # self.tilt_servo = picar.Servo.Servo(2)
        # self.tilt_servo.offset = 20  # calibrate servo to center
        # self.tilt_servo.write(90)

        logging.debug('Set up back wheels')
        self.back_wheels = picar.back_wheels.Back_Wheels()
        self.back_wheels.speed = 0  # Speed Range is 0 (stop) - 100 (fastest)

        logging.debug('Set up front wheels')
        self.front_wheels = picar.front_wheels.Front_Wheels()
        self.front_wheels.turning_offset = 10  # calibrate servo to center
        self.front_wheels.turn(90)  # Steering Range is 45 (left) - 90 (center) - 135 (right)

        self.lane_follower = HandCodedLaneFollower(self)

        logging.info('Created a DeepPiCar')

    def create_video_recorder(self, path):
        return cv2.VideoWriter(path, self.fourcc, 20.0, (self.__SCREEN_WIDTH, self.__SCREEN_HEIGHT))

    def __enter__(self):
        """ Entering a with statement """
        return self

    def __exit__(self, _type, value, traceback):
        """ Exit a with statement"""
        if traceback is not None:
            # Exception occurred:
            logging.error('Exiting with statement with exception %s' % traceback)

        self.cleanup()

    def cleanup(self):
        """ Reset the hardware"""
        logging.info('Stopping the car, resetting hardware.')
        self.back_wheels.speed = 0
        self.front_wheels.turn(90)
        self.camera.release()
        #self.video_orig.release()
        #self.video_lane.release()
        cv2.destroyAllWindows()

    def drive(self, speed=__INITIAL_SPEED):
        """ Main entry point of the car, and put it in drive mode

        Keyword arguments:
        speed -- speed of back wheel, range is 0 (stop) - 100 (fastest)
        """

        logging.info('Starting to drive at speed %s...' % speed)
        #self.back_wheels.speed = speed
        self.back_wheels.speed = speed
        while self.camera.isOpened():
            
            _, image_lane = self.camera.read()
            #image_objs = image_lane.copy()
            #self.video_orig.write(image_lane)

            image_lane = self.follow_lane(image_lane)
            
            #self.video_lane.write(image_lane)
            #show_image('Lane Lines', image_lane)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.cleanup()
                break

    def follow_lane(self, image):
        image = self.lane_follower.follow_lane(image)
        return image


############################
# Utility Functions
############################
def show_image(title, frame, show=_SHOW_IMAGE):
    if show:
        cv2.imshow(title, frame)

def network_thread():
    bufferSize  = 1024

    UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    UDPServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    UDPServerSocket.bind(("", 5000))
    print("UDP server up and listening")
    while(True):
        bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
        message = bytesAddressPair[0]
        address = bytesAddressPair[1]
        clientMsg = "Message from Client:{}".format(message)
        clientIP  = "Client IP Address:{}".format(address)
        print(clientMsg)
        print(clientIP)
        global car
        car.back_wheels.speed = 20


def main():
    global car
    with DeepPiCar() as car:
        thread = Thread(target=network_thread, daemon=True).start()
        car.drive(40)


if __name__ == '__main__':
    main()
