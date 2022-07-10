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

from hsv_widget import *
from settings_widget import *
from video_stream import ThreadRunStream

drone = tellopy.Tello()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.colorUpper = (74, 203, 164)
        self.colorLower = (62, 89, 75)
        self.video_thread = None
        self.setWindowTitle("Tello Drohne")
        left_frame = QFrame(self)
        left_frame.setFrameShape(QFrame.StyledPanel)
        right_frame = QFrame(self)
        right_frame.setFrameShape(QFrame.StyledPanel)
        splitter = QSplitter(QtCore.Qt.Horizontal)
        splitter.addWidget(left_frame)
        splitter.addWidget(right_frame)
        splitter.setSizes([60, 200])
        bottom_frame = QFrame(self)
        bottom_frame.setFrameShape(QFrame.StyledPanel)
        splitter_bottom = QSplitter(Qt.Vertical)
        splitter_bottom.addWidget(splitter)
        splitter_bottom.addWidget(bottom_frame)
        splitter_bottom.setSizes([300, 50])

        self.btn_connect = QPushButton("Take off")
        self.btn_connect.clicked.connect(self.button_connect)
        self.btn_connect.setDisabled(True)
        self.btn_stream = QPushButton("Start stream")
        self.btn_stream.clicked.connect(self.button_stream)
        self.btn_disconnect = QPushButton("Stop")
        self.btn_disconnect.clicked.connect(self.button_disconnect)
        self.btn_disconnect.setDisabled(True)
        self.btn_battery = QPushButton("State")
        self.btn_battery.clicked.connect(self.button_check_battery)
        self.btn_refresh = QPushButton("Refresh")
        self.btn_refresh.clicked.connect(self.checkWifi)
        layout_left = QVBoxLayout()
        # layout_left.setAlignment(QtCore.Qt.AlignTop)
        layout_left.addWidget(self.btn_connect)
        layout_left.addWidget(self.btn_stream)
        layout_left.addWidget(self.btn_disconnect)
        layout_left.addWidget(self.btn_battery)
        layout_left.addWidget(self.btn_refresh, alignment=QtCore.Qt.AlignBottom)
        left_frame.setLayout(layout_left)

        self.tab_1 = QLabel("Press 'Connect' to start")
        self.tab_1.setAlignment(Qt.AlignCenter)
        self.tab_2 = HsvWidget(window=self, drone=drone)
        self.right_widget = QTabWidget()
        self.tab_3 = SettingsWidget(window=self)
        self.right_widget = QTabWidget()
        self.right_widget.addTab(self.tab_1, "Video stream")
        self.right_widget.addTab(self.tab_2, "HSV Color")
        self.right_widget.addTab(self.tab_3, "Settings")
        # self.right_widget.setTabEnabled(1, False)

        # self.label.setAlignment(Qt.AlignCenter)
        self.tab_1.setContentsMargins(0, 0, 0, 0)
        layout_right = QVBoxLayout()
        layout_right.addWidget(self.right_widget)
        right_frame.setLayout(layout_right)

        self.loggingTextBox = QPlainTextEdit()
        self.loggingTextBox.setStyleSheet("QTextEdit {color:red}")
        self.loggingTextBox.setReadOnly(True)

        self.loggingConsole = QPlainTextEdit()
        self.loggingConsole.setStyleSheet("QTextEdit {color:red}")
        self.loggingConsole.setReadOnly(True)

        layout_bottom = QHBoxLayout()
        layout_bottom.addWidget(self.loggingTextBox)
        layout_bottom.addWidget(self.loggingConsole)
        layout_bottom.setContentsMargins(0, 0, 0, 0)
        bottom_frame.setLayout(layout_bottom)

        main_layout = QHBoxLayout()
        main_layout.addWidget(splitter_bottom)
        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        self.setGeometry(400, 200, 1100, 700)
        self.setFixedWidth(1100)
        self.setFixedHeight(740)
        self.checkWifi()
        self.show()
        self.loadHsvValues()

    def loadHsvValues(self):
        with open('hsv.json') as f:
            data = json.load(f)
            self.colorUpper = tuple(data["hsv"]["colorUpper"])
            self.colorLower = tuple(data["hsv"]["colorLower"])

    def updateLowerUpper(self, lower, upper):
        self.colorLower = lower
        self.colorUpper = upper
        if self.video_thread is not None:
            self.video_thread.updateLowerUpper(self.colorLower, self.colorUpper)

    def addNewLogLine(self, text):
        self.loggingTextBox.appendPlainText(text)
        self.loggingTextBox.verticalScrollBar().maximum()

    def checkWifi(self):
        wifi = subprocess.check_output(['netsh', 'WLAN', 'show', 'interfaces'])
        if b"TELLO" in wifi:
            self.addNewLogLine("TELLO drone WIFI connected")
            #self.btn_connect.setDisabled(False)
            self.btn_stream.setDisabled(False)
            #self.btn_disconnect.setDisabled(False)
            self.btn_battery.setDisabled(False)
        else:
            self.addNewLogLine("TELLO drone is not connected. Hit refresh to check again")
            self.btn_connect.setDisabled(True)
            self.btn_stream.setDisabled(True)
            self.btn_disconnect.setDisabled(True)
            self.btn_battery.setDisabled(True)

    @pyqtSlot(QImage)
    def setStream(self, image):
        # Video in PyQt5 in other thread:
        # https://stackoverflow.com/questions/44404349/pyqt-showing-video-stream-from-opencv
        self.tab_1.setPixmap(QPixmap.fromImage(image))

    def button_connect(self):
        drone.connect()
        drone.takeoff()
        self.btn_disconnect.setDisabled(False)
        self.btn_connect.setDisabled(True)
        self.right_widget.setTabEnabled(1, False)
        #self.video_thread.setstartroutine(self)


    def button_stream(self):
        QApplication.processEvents()
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.addNewLogLine("Starting video stream...")
        self.video_thread = ThreadRunStream.instance()
        self.video_thread.set_params(self, drone, self.colorUpper, self.colorLower)
        self.video_thread.videoStream.connect(self.setStream)
        self.video_thread.start()
        self.btn_connect.setDisabled(False)
        self.right_widget.setTabEnabled(1, True)
        self.btn_stream.setDisabled(True)

    def button_disconnect(self):
        self.addNewLogLine("Landing...")
        self.btn_connect.setDisabled(False)
        self.btn_disconnect.setDisabled(True)
        self.right_widget.setTabEnabled(1,True)
        drone.land()

    def button_check_battery(self):
        drone.connect()
        self.addNewLogLine(f"{drone.state}".replace("::", " "))
        QApplication.setOverrideCursor(Qt.ArrowCursor)
        #drone.clockwise(100)

    def closeEvent(self, event):
        self.video_thread.terminate()
        event.accept() # let the window close


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet("QTextEdit {color:red}")
    ex = MainWindow()
    sys.exit(app.exec_())