import sys

import imutils
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import *
from PyQt5 import Qt
from PyQt5.QtCore import QThread, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QImage, QPixmap
from djitellopy import tello
import cv2

import sys
import traceback
import tellopy
import av
import numpy
import time

import subprocess

drone = tellopy.Tello()
colorLower = (62, 89, 75)
colorUpper = (74, 203, 164)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Tello Drohne")
        left_frame = QFrame(self)
        left_frame.setFrameShape(QFrame.StyledPanel)
        right_frame = QFrame(self)
        right_frame.setFrameShape(QFrame.StyledPanel)
        splitter = QSplitter(QtCore.Qt.Horizontal)
        splitter.addWidget(left_frame)
        splitter.addWidget(right_frame)
        splitter.setSizes([80, 200])
        bottom_frame = QFrame(self)
        bottom_frame.setFrameShape(QFrame.StyledPanel)
        splitter_bottom = QSplitter(Qt.Vertical)
        splitter_bottom.addWidget(splitter)
        splitter_bottom.addWidget(bottom_frame)
        splitter_bottom.setSizes([300, 50])

        self.btn_connect = QPushButton("Connect")
        self.btn_connect.clicked.connect(self.button_connect)
        self.btn_disconnect = QPushButton("Disconnect")
        self.btn_disconnect.clicked.connect(self.button_disconnect)
        self.btn_battery = QPushButton("Check battery")
        self.btn_battery.clicked.connect(self.button_check_battery)
        self.btn_refresh = QPushButton("Refresh")
        self.btn_refresh.clicked.connect(self.checkWifi)
        layout_left = QVBoxLayout()
        # layout_left.setAlignment(QtCore.Qt.AlignTop)
        layout_left.addWidget(self.btn_connect)
        layout_left.addWidget(self.btn_disconnect)
        layout_left.addWidget(self.btn_battery)
        layout_left.addWidget(self.btn_refresh, alignment=QtCore.Qt.AlignBottom)
        left_frame.setLayout(layout_left)

        self.label = QLabel("Press 'Connect' to start")
        self.label.setAlignment(Qt.AlignCenter)
        layout_right = QVBoxLayout()
        layout_right.addWidget(self.label)
        right_frame.setLayout(layout_right)

        self.loggingTextBox = QPlainTextEdit()
        self.loggingTextBox.setStyleSheet("QTextEdit {color:red}")
        self.loggingTextBox.setReadOnly(True)
        # textBox.appendPlainText("testsdfasfasdfsadf")
        layout_bottom = QVBoxLayout()
        layout_bottom.addWidget(self.loggingTextBox)
        layout_bottom.setContentsMargins(0, 0, 0, 0)
        bottom_frame.setLayout(layout_bottom)

        main_layout = QHBoxLayout()
        main_layout.addWidget(splitter_bottom)
        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        self.setGeometry(500, 200, 1000, 650)

        self.checkWifi()
        self.show()

    def addNewLogLine(self, text):
        self.loggingTextBox.appendPlainText(text)
        self.loggingTextBox.verticalScrollBar().maximum()

    def checkWifi(self):
        wifi = subprocess.check_output(['netsh', 'WLAN', 'show', 'interfaces'])
        if b"TELLO" in wifi:
            self.addNewLogLine("TELLO drone connected")
            self.btn_battery.setDisabled(False)
            self.btn_connect.setDisabled(False)
        else:
            self.addNewLogLine("TELLO drone is not connected. Hit refresh to check again")
            self.btn_battery.setDisabled(True)
            self.btn_connect.setDisabled(True)

    @pyqtSlot(QImage)
    def setStream(self, image):
        # Video in PyQt5 in other thread:
        # https://stackoverflow.com/questions/44404349/pyqt-showing-video-stream-from-opencv
        self.label.setPixmap(QPixmap.fromImage(image))

    def button_connect(self):
        self.btn_connect.setDisabled(True)
        self.addNewLogLine("Starting video stream...")
        self.video_thread = ThreadRunStream(self)
        self.video_thread.changePixmap.connect(self.setStream)
        self.video_thread.start()

    def button_disconnect(self):
        self.btn_connect.setDisabled(False)
        self.addNewLogLine("Video stream paused. Hit 'Connect' to resume")
        self.video_thread.terminate()
        drone.land()

    def button_check_battery(self):
        drone.connect()
        self.addNewLogLine(f"Battery level: {drone.state}%")


class ThreadRunStream(QThread):
    changePixmap = pyqtSignal(QImage)

    def __init__(self, main_window):
        self.main_window = main_window
        self.keep_running = True
        drone.connect()
        super().__init__()

    def run(self):

        try:
            drone.connect()
            drone.takeoff()
            drone.wait_for_connection(60.0)

            retry = 3
            container = None
            while container is None and 0 < retry:
                retry -= 1
                try:
                    container = av.open(drone.get_video_stream())
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
                    # cv2.imshow('Original', image)
                    # cv2.imshow('Canny', cv2.Canny(image, 100, 200))
                    cv2.waitKey(1)
                    if frame.time_base < 1.0 / 60:
                        time_base = 1.0 / 60
                    else:
                        time_base = frame.time_base
                    frame_skip = int((time.time() - start_time) / time_base)

                    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
                    mask = cv2.inRange(hsv, colorLower, colorUpper)
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
                            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                            print(center)
                            # only proceed if the radius meets a minimum size
                            if radius > 5:
                                # draw the circle and centroid on the frame
                                cv2.circle(img, (int(x), int(y)), int(radius),
                                           (0, 255, 255), 2)
                                cv2.circle(img, center, 5, (0, 0, 255), -1)
                    self.trackball2(drone, center, radius)
                    # img = cv2.resize(img, (int(img.shape[0]*0.5), int(img.shape[1]*0.5)))
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    h, w, ch = img.shape
                    bytesPerLine = ch * w
                    convertToQtFormat = QImage(img.data, w, h, bytesPerLine, QImage.Format_RGB888)
                    p = convertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
                    self.changePixmap.emit(p)

            # if b"TELLO" not in subprocess.check_output(['netsh', 'WLAN', 'show', 'interfaces']):
            #     self.main_window.addNewLogLine("TELLO drone disconnected")
            #     self.keep_running = False

        except Exception as ex:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            print(ex)
        finally:
            drone.quit()
            cv2.destroyAllWindows()


    def trackball2(self, me, center, radius):
        print(f"BALL: {center} - {radius}")
        if center is None:
            drone.clockwise(0)
            drone.forward(0)
        else:
            width = 640
            height = 480
            framecenter = (int(width // 2), int(height // 2))
            x_distance = center[0] - framecenter[0]
            x_distance = int(x_distance * 0.1)
            if x_distance > 100:
                x_distance = 100
            if x_distance > 15:
                drone.clockwise(abs(x_distance))
            elif x_distance < -15:
                drone.counter_clockwise(abs(x_distance))
            else:
                drone.clockwise(0)
                # print(radius)
                if radius > 15 and radius < 50:
                    drone.forward(0)
                elif radius < 15:
                    # velocity = int(50/radius)
                    drone.forward(20)
                elif radius > 50:
                    # velocity = int(40-radius)
                    drone.backward(20)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet("QTextEdit {color:red}")
    ex = MainWindow()
    sys.exit(app.exec_())