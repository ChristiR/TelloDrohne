import sys

import imutils
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import *
from PyQt5 import Qt
from PyQt5.QtCore import QThread, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QImage, QPixmap
import cv2

import sys
import traceback
import av
import numpy
import time

import subprocess

from hsv_widget import *
from utils import *

FILE_NAME = "picture.png"


@Singleton
# singleton is needed here, otherwise there will be an error when clicking on "Start stream" multiple times
# ( -> multiple instances of the this thread doesnt work)
class ThreadRunStream(QThread):
    videoStream = pyqtSignal(QImage)
    hsvImage = pyqtSignal(QImage)
    # Parametereinstellung Standardwerte
    # Clockwise/Counter_Clockwise
    max_velocity_clockwise = 60
    max_distance_x_clockwise = 210
    min_distance_x_clockwise = 30

    max_velocity_counter_clockwise = 60
    max_distance_x_counter_clockwise = 210
    min_distance_x_counter_clockwise = 30

    # Forward/Backward
    max_velocity_forward = 60
    max_radius_forward = 40
    min_radius_forward = 20

    max_velocity_backward = 60
    max_radius_backward = 200
    min_radius_backward = 70

    # Up/Down
    max_velocity_up = 50
    max_distance_y_up = 150
    min_distance_y_up = 35

    max_velocity_down = 50
    max_distance_y_down = 150
    min_distance_y_down = 35
    turn = 0
    def __init__(self):
        self.emit_one_pic = False
        super().__init__()

    def set_params(self, main_window, drone, upper, lower):
        drone.connect()
        self.main_window = main_window
        self.drone = drone
        self.colorUpper = upper
        self.colorLower = lower

    def updateLowerUpper(self, lower, upper):
        self.colorLower = lower
        self.colorUpper = upper
        print("UPDSATED")
        print(self.colorLower)
        print(self.colorUpper)
    def stop(self):
        self.terminate()

    def run(self):
        try:
            self.drone.wait_for_connection(60.0)
            retry = 3
            container = None
            while container is None and 0 < retry:
                retry -= 1
                try:
                    container = av.open(self.drone.get_video_stream())
                except av.AVError as ave:
                    print(ave)
                    print('retry...')

            # skip first 300 frames
            frame_skip = 300
            while True:
                for frame in container.decode(video=0):
                    if 0 < frame_skip:
                        frame_skip = frame_skip - 1
                        continue
                    start_time = time.time()
                    img = cv2.cvtColor(numpy.array(frame.to_image()), cv2.COLOR_RGB2BGR)

                    # this is for emitting one pic to the hsv tool
                    if self.emit_one_pic:
                        self.emit_one_pic = False
                        cv2.imwrite(FILE_NAME, img)
                        img_new = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                        h, w, ch = img_new.shape
                        bytesPerLine = ch * w
                        convertToQtFormat = QImage(img_new.data, w, h, bytesPerLine, QImage.Format_RGB888)
                        p = convertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
                        self.hsvImage.emit(p)

                    # cv2.imshow('Original', image)
                    # cv2.imshow('Canny', cv2.Canny(image, 100, 200))
                    # cv2.waitKey(1)
                    if frame.time_base < 1.0 / 60:
                        time_base = 1.0 / 60
                    else:
                        time_base = frame.time_base
                    frame_skip = int((time.time() - start_time) / time_base)

                    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
                    mask = cv2.inRange(hsv, self.colorLower, self.colorUpper)
                    print(self.colorLower)
                    print(self.colorUpper)
                    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    cnts = imutils.grab_contours(cnts)

                    center = None
                    radius = None
                    if len(cnts) > 0:
                        # find the largest contour in the mask, then use
                        # it to compute the minimum enclosing circle and
                        # centroid
                        c = max(cnts, key=cv2.contourArea)
                        ((x, y), radius) = cv2.minEnclosingCircle(c)
                        M = cv2.moments(c)
                        if M["m00"] != 0:
                            # only proceed if the radius meets a minimum size
                            if radius > 20:
                                # draw the circle and centroid on the frame
                                center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                                cv2.circle(img, (int(x), int(y)), int(radius), (0, 255, 0), 2)
                                cv2.circle(img, center, 5, (0, 255, 0), -1)

                    # # with hough circle detection
                    # img = cv2.medianBlur(img, 5)
                    # gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
                    # circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1.5, 10000, param1=70, param2=100, minRadius=20, maxRadius=400)
                    # print(f"CirclesHSV:   {center} - {radius}")
                    # print(f"CirclesHough: {circles}")
                    # if circles is not None:
                    #     for i in circles[0, :]:
                    #         cv2.circle(img, (int(i[0]), int(i[1])), int(i[2]), (0, 0, 255), 2) # draw the outer circle
                    #         cv2.circle(img, (int(i[0]), int(i[1])), 2, (0, 0, 255), 3) # draw the center of the circle
                    #
                    #         if radius is None:
                    #             center = (int(i[0]), int(i[1]))
                    #             radius = int(i[2])
                    #             print("HSV--NONE")
                    #         if int(i[2]) > radius:
                    #             center = (int(i[0]), int(i[1]))
                    #             radius = int(i[2])
                    #             print("HSV--smaller")


                    print(f"CircleUsed:   {center} - {radius}")
                    self.trackball(center, radius)
                    # img = cv2.resize(img, (int(img.shape[0]*0.5), int(img.shape[1]*0.5)))
                    img_new = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    h, w, ch = img_new.shape
                    bytesPerLine = ch * w
                    convertToQtFormat = QImage(img_new.data, w, h, bytesPerLine, QImage.Format_RGB888)
                    p = convertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
                    self.videoStream.emit(p)
                    # QApplication.restoreOverrideCursor()
                    QApplication.setOverrideCursor(Qt.ArrowCursor)
        except Exception as ex:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            print(ex)
            error_msg = str(exc_value)
            if "End of file" in error_msg:
                self.main_window.addNewLogLine("An internal error occured. Probably the drone turned off")
            self.main_window.addNewLogLine(f"ERROR: {error_msg}")
        finally:
            self.drone.quit()
            QApplication.setOverrideCursor(Qt.ArrowCursor)
            self.main_window.checkWifi()
            self.main_window.addNewLogLine("Could not connect to drone")


    def set_emit_one_pic(self):
        self.emit_one_pic = True

    def update_settings(self, v_u, dx_u, dn_u, v_d, dx_d, dn_d, v_c, dx_c, dn_c, v_cc, dx_cc, dn_cc, v_f, dx_f, dn_f, v_b, dx_b, dn_b):
        # Parametereinstellung Standardwerte
        # Clockwise/Counter_Clockwise
        self.max_velocity_clockwise = v_c
        self.max_distance_x_clockwise = dx_c
        self.min_distance_x_clockwise = dn_c

        self.max_velocity_counter_clockwise = v_cc
        self.max_distance_x_counter_clockwise = dx_cc
        self.min_distance_x_counter_clockwise = dn_cc

        # Forward/Backward
        self.max_velocity_forward = v_f
        self.max_radius_forward = dx_f
        self.min_radius_forward = dn_f

        self.max_velocity_backward = v_b
        self.max_radius_backward = dx_b
        self.min_radius_backward = dn_b

        # Up/Down
        self.max_velocity_up = v_u
        self.max_distance_y_up = dx_u
        self.min_distance_y_up = dn_u

        self.max_velocity_down = v_d
        self.max_distance_y_down = dx_d
        self.min_distance_y_down = dn_d

    def trackball(self, center, radius):
        if center is None:
            self.drone.clockwise(0)
            self.drone.forward(0)
            self.drone.up(0)
        else:
            width = 640
            height = 480
            framecenter = (int(width // 2), int(height // 2))
            x_distance = center[0] - framecenter[0]
            y_distance = center[1] - framecenter[1]
            self.turn = self.turn + 1
            if self.turn == 3:
                self.turn = 0
            if self.turn == 0:
                # rotation of drone
                #x_distance = 0
                if x_distance > self.min_distance_x_clockwise:
                    if x_distance > self.max_distance_x_clockwise:
                        velocity = self.max_velocity_clockwise
                    else:
                        velocity = int((self.max_velocity_clockwise / (self.max_distance_x_clockwise-self.min_distance_x_clockwise)) * (x_distance - self.min_distance_x_clockwise))
                    self.drone.clockwise(abs(velocity))
                elif x_distance < -self.min_distance_x_counter_clockwise:
                    if x_distance < -self.max_distance_x_counter_clockwise:
                        velocity = -self.max_velocity_counter_clockwise
                    else:
                        velocity = int((self.max_velocity_counter_clockwise / (self.max_distance_x_counter_clockwise-self.min_distance_x_counter_clockwise)) * (x_distance + self.min_distance_x_counter_clockwise))
                    self.drone.counter_clockwise(abs(velocity))
                else:
                    velocity = 0
                    self.drone.clockwise(velocity)
            if self.turn == 1:
                # forward and backward flying
                #radius = 42
                if radius > self.max_radius_forward and radius < self.min_radius_backward:
                    velocity = 0
                    self.drone.forward(velocity)
                elif radius < self.max_radius_forward:
                    if radius < self.min_radius_forward:
                        velocity = self.max_velocity_forward
                    else:
                        velocity = int((self.max_velocity_forward / (self.max_radius_forward - self.min_radius_forward)) * (radius - self.min_radius_forward))
                    # velocity = int(50/radius)
                    self.drone.forward(velocity)
                elif radius > self.min_radius_backward:
                    if radius > self.max_radius_backward:
                        velocity = self.max_velocity_backward
                    else:
                        velocity = int((self.max_velocity_backward / (self.max_radius_backward-self.min_radius_backward)) * (radius - self.min_radius_backward))
                    # velocity = int(40-radius)
                    self.drone.backward(velocity)
            if self.turn == 2:
                # flying up and down
                #y_distance = 0
                if y_distance > self.min_distance_y_down:
                    if y_distance > self.max_distance_y_down:
                        velocity = self.max_velocity_down
                    else:
                        velocity = int((self.max_velocity_down / (self.max_distance_y_down-self.min_distance_y_down)) * (y_distance - self.min_distance_y_down))
                    self.drone.down(abs(velocity))
                elif y_distance < -self.min_distance_y_up:
                    if y_distance < -self.max_distance_y_up:
                        velocity = -self.max_velocity_up
                    else:
                        velocity = int((self.max_velocity_up / (self.max_distance_y_up-self.min_distance_y_up)) * (y_distance + self.min_distance_y_up))
                    self.drone.up(abs(velocity))
                else:
                    velocity = 0
                    self.drone.up(velocity)







