import sys
import os
import base64

from PyQt5 import uic
from PyQt5 import QtGui
from PyQt5.QtCore import QSize, QThread
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QThread, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QColor, QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QCheckBox, QComboBox, QFileDialog, QMainWindow, QLabel, QPushButton, QSlider, \
    QWidget, QHBoxLayout, QLineEdit
import cv2
import numpy as np
import os


class SettingsWidget(QWidget):

    # Up/Down
    max_velocity_up = 50
    max_distance_y_up = 150
    min_distance_y_up = 35

    max_velocity_down = 50
    max_distance_y_down = 150
    min_distance_y_down = 35

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



    def __init__(self, window):
        super(SettingsWidget, self).__init__()
        self.window = window
        uic.loadUi(os.path.join(os.path.dirname(__file__), "./assets/settings_window.ui"), self)
        #buttons
        self.b_save = self.findChild(QPushButton, "b_save")
        self.b_reset = self.findChild(QPushButton, "b_reset")
        #Sliders
        self.s_max_vel_up = self.findChild(QSlider, "s_max_vel_up")
        self.s_min_dis_up = self.findChild(QSlider, "s_min_dis_up")
        self.s_max_dis_up = self.findChild(QSlider, "s_max_dis_up")

        self.s_max_vel_down = self.findChild(QSlider, "s_max_vel_down")
        self.s_min_dis_down = self.findChild(QSlider, "s_min_dis_down")
        self.s_max_dis_down = self.findChild(QSlider, "s_max_dis_down")

        self.s_max_vel_clockwise = self.findChild(QSlider, "s_max_vel_clockwise")
        self.s_min_dis_clockwise = self.findChild(QSlider, "s_min_dis_clockwise")
        self.s_max_dis_clockwise = self.findChild(QSlider, "s_max_dis_clockwise")

        self.s_max_vel_counter_clockwise = self.findChild(QSlider, "s_max_vel_counter_clockwise")
        self.s_min_dis_counter_clockwise = self.findChild(QSlider, "s_min_dis_counter_clockwise")
        self.s_max_dis_counter_clockwise = self.findChild(QSlider, "s_max_dis_counter_clockwise")

        self.s_max_vel_forward = self.findChild(QSlider, "s_max_vel_forward")
        self.s_min_dis_forward = self.findChild(QSlider, "s_min_dis_forward")
        self.s_max_dis_forward = self.findChild(QSlider, "s_max_dis_forward")

        self.s_max_vel_backward = self.findChild(QSlider, "s_max_vel_backward")
        self.s_min_dis_backward = self.findChild(QSlider, "s_min_dis_backward")
        self.s_max_dis_backward = self.findChild(QSlider, "s_max_dis_backward")

        #LineEdit
        self.e_max_vel_up = self.findChild(QLineEdit, "e_max_vel_up")
        self.e_min_dis_up = self.findChild(QLineEdit, "e_min_dis_up")
        self.e_max_dis_up = self.findChild(QLineEdit, "e_max_dis_up")

        self.e_max_vel_down = self.findChild(QLineEdit, "e_max_vel_down")
        self.e_min_dis_down = self.findChild(QLineEdit, "e_min_dis_down")
        self.e_max_dis_down = self.findChild(QLineEdit, "e_max_dis_down")

        self.e_max_vel_clockwise = self.findChild(QLineEdit, "e_max_vel_clockwise")
        self.e_min_dis_clockwise = self.findChild(QLineEdit, "e_min_dis_clockwise")
        self.e_max_dis_clockwise = self.findChild(QLineEdit, "e_max_dis_clockwise")

        self.e_max_vel_counter_clockwise = self.findChild(QLineEdit, "e_max_vel_counter_clockwise")
        self.e_min_dis_counter_clockwise = self.findChild(QLineEdit, "e_min_dis_counter_clockwise")
        self.e_max_dis_counter_clockwise = self.findChild(QLineEdit, "e_max_dis_counter_clockwise")

        self.e_max_vel_forward = self.findChild(QLineEdit, "e_max_vel_forward")
        self.e_min_dis_forward = self.findChild(QLineEdit, "e_min_dis_forward")
        self.e_max_dis_forward = self.findChild(QLineEdit, "e_max_dis_forward")

        self.e_max_vel_backward = self.findChild(QLineEdit, "e_max_vel_backward")
        self.e_min_dis_backward = self.findChild(QLineEdit, "e_min_dis_backward")
        self.e_max_dis_backward = self.findChild(QLineEdit, "e_max_dis_backward")

        self.init_handler()


    def init_handler(self):
        self.b_save.clicked.connect(self.onBtnSaveClicked)
        self.b_reset.clicked.connect(self.onBtnResetClicked)
        self.s_max_vel_up.valueChanged.connect(self.on_s_max_vel_up_Changed)
        self.s_min_dis_up.valueChanged.connect(self.on_s_min_dis_up_Changed)
        self.s_max_dis_up.valueChanged.connect(self.on_s_max_dis_up_Changed)

        self.s_max_vel_down.valueChanged.connect(self.on_s_max_vel_down_Changed)
        self.s_min_dis_down.valueChanged.connect(self.on_s_min_dis_down_Changed)
        self.s_max_dis_down.valueChanged.connect(self.on_s_max_dis_down_Changed)

        self.s_max_vel_clockwise.valueChanged.connect(self.on_s_max_vel_clockwise_Changed)
        self.s_min_dis_clockwise.valueChanged.connect(self.on_s_min_dis_clockwise_Changed)
        self.s_max_dis_clockwise.valueChanged.connect(self.on_s_max_dis_clockwise_Changed)

        self.s_max_vel_counter_clockwise.valueChanged.connect(self.on_s_max_vel_counter_clockwise_Changed)
        self.s_min_dis_counter_clockwise.valueChanged.connect(self.on_s_min_dis_counter_clockwise_Changed)
        self.s_max_dis_counter_clockwise.valueChanged.connect(self.on_s_max_dis_counter_clockwise_Changed)

        self.s_max_vel_forward.valueChanged.connect(self.on_s_max_vel_forward_Changed)
        self.s_min_dis_forward.valueChanged.connect(self.on_s_min_dis_forward_Changed)
        self.s_max_dis_forward.valueChanged.connect(self.on_s_max_dis_forward_Changed)

        self.s_max_vel_backward.valueChanged.connect(self.on_s_max_vel_backward_Changed)
        self.s_min_dis_backward.valueChanged.connect(self.on_s_min_dis_backward_Changed)
        self.s_max_dis_backward.valueChanged.connect(self.on_s_max_dis_backward_Changed)

    def onBtnSaveClicked(self):
        try:
            self.image_thread = self.window.video_thread
            #v_u, dx_u, dn_u, v_d, dx_d, dn_d, v_c, dx_c, dn_c, v_cc, dx_cc, dn_cc, v_f, dx_f, dn_f, v_b, dx_b, dn_b)
            self.image_thread.update_settings(self.max_velocity_up, self.max_distance_y_up, self.min_distance_y_up, self.max_velocity_down, self.max_distance_y_down, self.min_distance_y_down, self.max_velocity_clockwise, self.max_distance_x_clockwise, self.min_distance_x_clockwise, self.max_velocity_counter_clockwise, self.max_distance_x_counter_clockwise, self.min_distance_x_counter_clockwise, self.max_velocity_forward, self.max_radius_forward, self. min_radius_forward, self.max_velocity_backward, self.max_radius_backward, self.min_radius_backward)
            self.window.addNewLogLine(
                f"New values set for Up\n\tMax. Velocity: {self.max_velocity_up}\n\tMin. Distance: {self.min_distance_y_up}\n\tMax. Distance: {self.max_distance_y_up}")
            self.window.addNewLogLine(
                f"New values set for Down\n\tMax. Velocity: {self.max_velocity_down}\n\tMin. Distance: {self.min_distance_y_down}\n\tMax. Distance: {self.max_distance_y_down}")
            self.window.addNewLogLine(
                f"New values set for Counter_Clockwise\n\tMax. Velocity: {self.max_velocity_counter_clockwise}\n\tMin. Distance: {self.min_distance_x_counter_clockwise}\n\tMax. Distance: {self.max_distance_x_counter_clockwise}")
            self.window.addNewLogLine(
                f"New values set for Clockwise\n\tMax. Velocity: {self.max_velocity_clockwise}\n\tMin. Distance: {self.min_distance_x_clockwise}\n\tMax. Distance: {self.max_distance_x_clockwise}")
            self.window.addNewLogLine(
                f"New values set for Forward\n\tMax. Velocity: {self.max_velocity_forward}\n\tMin. Radius: {self.min_radius_forward}\n\tMax. Radius: {self.max_radius_forward}")
            self.window.addNewLogLine(
                f"New values set for Backward\n\tMax. Velocity: {self.max_velocity_backward}\n\tMin. Radius: {self.min_radius_backward}\n\tMax. Radius: {self.max_radius_backward}")
        except Exception as ex:
            self.window.addNewLogLine(f"Video stream must be running")

    def onBtnResetClicked(self):
        # Up/Down
        max_velocity_up = 50
        self.s_max_vel_up.setValue(max_velocity_up)
        max_distance_y_up = 150
        self.s_max_dis_up.setValue(max_distance_y_up)
        min_distance_y_up = 35
        self.s_min_dis_up.setValue(min_distance_y_up)

        max_velocity_down = 50
        self.s_max_vel_down.setValue(max_velocity_down)
        max_distance_y_down = 150
        self.s_max_dis_down.setValue(max_distance_y_down)
        min_distance_y_down = 35
        self.s_min_dis_down.setValue(min_distance_y_down)

        # Clockwise/Counter_Clockwise
        max_velocity_clockwise = 60
        self.s_max_vel_clockwise.setValue(max_velocity_clockwise)
        max_distance_x_clockwise = 210
        self.s_max_dis_clockwise.setValue(max_distance_x_clockwise)
        min_distance_x_clockwise = 30
        self.s_min_dis_clockwise.setValue(min_distance_x_clockwise)

        max_velocity_counter_clockwise = 60
        self.s_max_vel_counter_clockwise.setValue(max_velocity_counter_clockwise)
        max_distance_x_counter_clockwise = 210
        self.s_max_dis_counter_clockwise.setValue(max_distance_x_counter_clockwise)
        min_distance_x_counter_clockwise = 30
        self.s_min_dis_counter_clockwise.setValue(min_distance_x_counter_clockwise)

        # Forward/Backward
        max_velocity_forward = 60
        self.s_max_vel_forward.setValue(max_velocity_forward)
        max_radius_forward = 40
        self.s_max_dis_forward.setValue(max_radius_forward)
        min_radius_forward = 20
        self.s_min_dis_forward.setValue(min_radius_forward)

        max_velocity_backward = 60
        self.s_max_vel_backward.setValue(max_velocity_backward)
        max_radius_backward = 200
        self.s_max_dis_backward.setValue(max_radius_backward)
        min_radius_backward = 70
        self.s_min_dis_backward.setValue(min_radius_backward)
        self.window.addNewLogLine(f"All values have been reset to default values.")

    def on_s_max_vel_up_Changed(self):
        _v = self.selectedValue = self.s_max_vel_up.value()
        self.max_velocity_up = _v
        self.e_max_vel_up.setText(str(_v))

    def on_s_min_dis_up_Changed(self):
        self.s_max_dis_up.setMinimum(self.s_min_dis_up.value())
        self.s_min_dis_up.setMaximum(self.s_max_dis_up.value())
        _v = self.selectedValue = self.s_min_dis_up.value()
        self.min_distance_y_up = _v
        self.e_min_dis_up.setText(str(_v))

    def on_s_max_dis_up_Changed(self):
        self.s_max_dis_up.setMinimum(self.s_min_dis_up.value())
        self.s_min_dis_up.setMaximum(self.s_max_dis_up.value())
        _v = self.selectedValue = self.s_max_dis_up.value()
        self.max_distance_y_up = _v
        self.e_max_dis_up.setText(str(_v))

    def on_s_max_vel_down_Changed(self):
        _v = self.selectedValue = self.s_max_vel_down.value()
        self.max_velocity_down = _v
        self.e_max_vel_down.setText(str(_v))

    def on_s_min_dis_down_Changed(self):
        self.s_max_dis_down.setMinimum(self.s_min_dis_down.value())
        self.s_min_dis_down.setMaximum(self.s_max_dis_down.value())
        _v = self.selectedValue = self.s_min_dis_down.value()
        self.min_distance_y_down = _v
        self.e_min_dis_down.setText(str(_v))

    def on_s_max_dis_down_Changed(self):
        self.s_max_dis_down.setMinimum(self.s_min_dis_down.value())
        self.s_min_dis_down.setMaximum(self.s_max_dis_down.value())
        _v = self.selectedValue = self.s_max_dis_down.value()
        self.max_distance_y_down = _v
        self.e_max_dis_down.setText(str(_v))

    def on_s_max_vel_clockwise_Changed(self):
        _v = self.selectedValue = self.s_max_vel_clockwise.value()
        self.max_velocity_clockwise = _v
        self.e_max_vel_clockwise.setText(str(_v))

    def on_s_min_dis_clockwise_Changed(self):
        self.s_max_dis_clockwise.setMinimum(self.s_min_dis_clockwise.value())
        self.s_min_dis_clockwise.setMaximum(self.s_max_dis_clockwise.value())
        _v = self.selectedValue = self.s_min_dis_clockwise.value()
        self.min_distance_x_clockwise = _v
        self.e_min_dis_clockwise.setText(str(_v))

    def on_s_max_dis_clockwise_Changed(self):
        self.s_max_dis_clockwise.setMinimum(self.s_min_dis_clockwise.value())
        self.s_min_dis_clockwise.setMaximum(self.s_max_dis_clockwise.value())
        _v = self.selectedValue = self.s_max_dis_clockwise.value()
        self.max_distance_x_clockwise = _v
        self.e_max_dis_clockwise.setText(str(_v))

    def on_s_max_vel_counter_clockwise_Changed(self):
        _v = self.selectedValue = self.s_max_vel_counter_clockwise.value()
        self.max_velocity_counter_clockwise = _v
        self.e_max_vel_counter_clockwise.setText(str(_v))

    def on_s_min_dis_counter_clockwise_Changed(self):
        self.s_max_dis_counter_clockwise.setMinimum(self.s_min_dis_counter_clockwise.value())
        self.s_min_dis_counter_clockwise.setMaximum(self.s_max_dis_counter_clockwise.value())
        _v = self.selectedValue = self.s_min_dis_counter_clockwise.value()
        self.min_distance_x_counter_clockwise = _v
        self.e_min_dis_counter_clockwise.setText(str(_v))

    def on_s_max_dis_counter_clockwise_Changed(self):
        self.s_max_dis_counter_clockwise.setMinimum(self.s_min_dis_counter_clockwise.value())
        self.s_min_dis_counter_clockwise.setMaximum(self.s_max_dis_counter_clockwise.value())
        _v = self.selectedValue = self.s_max_dis_counter_clockwise.value()
        self.min_distance_x_counter_clockwise = _v
        self.e_max_dis_counter_clockwise.setText(str(_v))

    def on_s_max_vel_forward_Changed(self):
        _v = self.selectedValue = self.s_max_vel_forward.value()
        self.max_velocity_forward = _v
        self.e_max_vel_forward.setText(str(_v))

    def on_s_min_dis_forward_Changed(self):
        self.s_min_dis_forward.setMaximum(self.s_max_dis_forward.value())
        self.s_max_dis_forward.setMinimum(self.s_min_dis_forward.value())
        _v = self.selectedValue = self.s_min_dis_forward.value()
        self.min_radius_forward = _v
        self.e_min_dis_forward.setText(str(_v))

    def on_s_max_dis_forward_Changed(self):
        self.s_min_dis_forward.setMaximum(self.s_max_dis_forward.value())
        self.s_min_dis_backward.setMinimum(self.s_max_dis_forward.value())
        self.s_max_dis_forward.setMinimum(self.s_min_dis_forward.value())
        self.s_max_dis_forward.setMaximum(self.s_min_dis_backward.value())
        _v = self.selectedValue = self.s_max_dis_forward.value()
        self.max_radius_forward = _v
        self.e_max_dis_forward.setText(str(_v))

    def on_s_max_vel_backward_Changed(self):
        _v = self.selectedValue = self.s_max_vel_backward.value()
        self.max_velocity_backward = _v
        self.e_max_vel_backward.setText(str(_v))

    def on_s_min_dis_backward_Changed(self):
        self.s_max_dis_forward.setMaximum(self.s_min_dis_backward.value())
        self.s_max_dis_backward.setMinimum(self.s_min_dis_backward.value())
        self.s_min_dis_backward.setMinimum(self.s_max_dis_forward.value())
        self.s_min_dis_backward.setMaximum(self.s_max_dis_backward.value())
        _v = self.selectedValue = self.s_min_dis_backward.value()
        self.min_radius_backward = _v
        self.e_min_dis_backward.setText(str(_v))

    def on_s_max_dis_backward_Changed(self):
        self.s_max_dis_backward.setMinimum(self.s_min_dis_backward.value())
        self.s_min_dis_backward.setMaximum(self.s_max_dis_backward.value())
        _v = self.selectedValue = self.s_max_dis_backward.value()
        self.max_radius_backward = _v
        self.e_max_dis_backward.setText(str(_v))

