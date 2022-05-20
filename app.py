import sys

import imutils
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import *
from PyQt5 import Qt
from PyQt5.QtCore import QThread, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QImage, QPixmap
from djitellopy import tello
import cv2

import subprocess


me = tello.Tello()
colorLower = (61, 90, 87)
colorUpper = (80, 214, 190)

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
        me.land()
        me.streamoff()

    def button_check_battery(self):
        me.connect()
        self.addNewLogLine(f"Battery level: {me.get_battery()}%")


class ThreadRunStream(QThread):
    changePixmap = pyqtSignal(QImage)

    def __init__(self, main_window):
        self.main_window = main_window
        self.keep_running = True
        me.connect()
        super().__init__()

    def trackball(self, me, center, radius):
        width = 640
        height = 480
        framecenter = (int(width // 2), int(height // 2))
        lr = 0
        vr = 0
        hr = 0
        speed = 0
        if center[0] > framecenter[0]:
            # ball rechts von mitte
            # print("RECHTS")
            # lr = 0
            # if center[0] > 350:
            #     lr = 10
            # if center[0] > 400:
            #     lr = 25
            # if center[0] > 450:
            #     lr = 35
            # if center[0] > 500:
            #     lr = 50
            # if center[0] > 550:
            #     lr = 75
            # if center[0] > 600:
            #     lr = 100
            lr1 = 0
            if center[0] > 350:
                lr1 = 10
            if center[0] > 400:
                lr1 = 25
            if center[0] > 450:
                lr1 = 35
            if center[0] > 500:
                lr1 = 50
            if center[0] > 550:
                lr1 = 75
            if center[0] > 600:
                lr1 = 100
            if lr1 != 0:
                me.rotate_clockwise(lr1)
        if center[0] < framecenter[0]:
            # ball links von mitte
            # print("LINKS")
            # lr = 0
            # if center[0] < 290:
            #     lr = -10
            # if center[0] < 240:
            #     lr = -25
            # if center[0] < 190:
            #     lr = -35
            # if center[0] < 140:
            #     lr = -50
            # if center[0] < 90:
            #     lr = -75
            # if center[0] < 40:
            #     lr = -100
            lr2 = 0
            if center[0] < 290:
                lr2 = 10
            if center[0] < 240:
                lr2 = 25
            if center[0] < 190:
                lr2 = 35
            if center[0] < 140:
                lr2 = 50
            if center[0] < 90:
                lr2 = 75
            if center[0] < 40:
                lr2 = 100
            if lr2 != 0:
                me.rotate_counter_clockwise(lr2)
        if center[1] < framecenter[1]:
            # ball über mitte
            # print("RUNTER")
            hr = 0
            if center[1] < 180:
                hr = 10
            if center[1] < 150:
                hr = 25
            if center[1] < 120:
                hr = 50
            if center[1] < 90:
                hr = 75
            if center[1] < 60:
                hr = 100
            me.send_rc_control(lr, vr, hr, speed)
        if center[1] > framecenter[1]:
            # ball unter mitte
            # print("HOCH")
            hr = 0
            if center[1] > 300:
                hr = -10
            if center[1] > 330:
                hr = -25
            if center[1] > 360:
                hr = -50
            if center[1] > 390:
                hr = -75
            if center[1] > 420:
                hr = -100
            me.send_rc_control(lr, vr, hr, speed)
        if radius < 1:
            # ball bewegt sich weg
            # print("VORWÄRTS")
            vr = 0  # -10
        if radius > 1:
            # ball bewegt sich auf drohne zu
            # print("RÜCKWÄRTS")
            vr = 0  # 10
        speed = 10

    def run(self):
        me.takeoff()
        if not me.stream_on:
            me.streamon()
            me.set_video_fps('high')
            me.set_video_bitrate(5)
            me.set_video_resolution('low')

        while self.keep_running:
            # https://stackoverflow.com/a/55468544/6622587
            img = me.get_frame_read().frame
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(hsv, colorLower, colorUpper)
            cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                                    cv2.CHAIN_APPROX_SIMPLE)
            cnts = imutils.grab_contours(cnts)
            if len(cnts) > 0:
                # find the largest contour in the mask, then use
                # it to compute the minimum enclosing circle and
                # centroid
                c = max(cnts, key=cv2.contourArea)
                ((x, y), radius) = cv2.minEnclosingCircle(c)
                M = cv2.moments(c)
                if M["m00"] != 0:
                    center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                # print(center)
                # only proceed if the radius meets a minimum size
                if radius > 5:
                    # draw the circle and centroid on the frame
                    cv2.circle(img, (int(x), int(y)), int(radius),
                               (0, 255, 255), 2)
                    cv2.circle(img, center, 5, (0, 0, 255), -1)
                self.trackball(me, center, radius)

            # img = cv2.resize(img, (int(img.shape[0]*0.5), int(img.shape[1]*0.5)))
            # rgbImage = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            h, w, ch = img.shape
            bytesPerLine = ch * w
            convertToQtFormat = QImage(img.data, w, h, bytesPerLine, QImage.Format_RGB888)
            p = convertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
            self.changePixmap.emit(p)
            if b"TELLO" not in subprocess.check_output(['netsh', 'WLAN', 'show', 'interfaces']):
                self.main_window.addNewLogLine("TELLO drone disconnected")
                self.keep_running = False


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet("QTextEdit {color:red}")
    ex = MainWindow()
    sys.exit(app.exec_())