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
    QWidget, QHBoxLayout
import cv2
import numpy as np
import os

import json

import sys
import traceback

import numpy as np
import av
import cv2
# import cv2_.cv2 as cv2
import numpy

FILE_NAME = "picture.png"


def generateSolidColorPixmap(w, h, color):
    canvas = QImage(QSize(w, h), QImage.Format_RGB30)
    for baris in range(0, h):
        for kolom in range(0, w):
            canvas.setPixel(kolom, baris, color.rgb())
    return canvas


class HsvWidget(QWidget):
    selectedHue = 0
    selectedSaturation = 255
    selectedValue = 255

    lowerHSV = (0, 0, 0)
    upperHSV = (179, 255, 255)

    imgRaw = None
    imgMask = None
    imgMasked = None

    imgHsvSpace = None

    def __init__(self, window, drone):
        super(HsvWidget, self).__init__()
        self.window = window
        self.drone = drone
        self.fileName = "picture.png"
        uic.loadUi(os.path.join(os.path.dirname(__file__), "./assets/main_window.ui"), self)

        self.sliderH = self.findChild(QSlider, "sliderH")
        self.sliderH.setMinimumWidth(165)
        self.sliderS = self.findChild(QSlider, "sliderS")
        self.sliderV = self.findChild(QSlider, "sliderV")

        self.lblH = self.findChild(QLabel, "lblH")
        self.lblS = self.findChild(QLabel, "lblS")
        self.lblV = self.findChild(QLabel, "lblV")

        self.lblLower = self.findChild(QLabel, "lblLower")
        self.lblUpper = self.findChild(QLabel, "lblUpper")

        self.previewH = self.findChild(QLabel, "previewH")
        self.previewS = self.findChild(QLabel, "previewS")
        self.previewV = self.findChild(QLabel, "previewV")

        self.previewRaw = self.findChild(QLabel, "previewRaw")
        self.previewRaw.setMinimumWidth(300)
        self.previewMask = self.findChild(QLabel, "previewMask")
        self.previewMaskedRaw = self.findChild(QLabel, "previewMaskedRaw")
        self.previewMaskedRaw.setMinimumWidth(300)
        self.previewHsvSpace = self.findChild(QLabel, "previewHsvSpace")

        self.cboxSetMode = self.findChild(QComboBox, "cboxSetMode")

        self.btnOpen = self.findChild(QPushButton, "btnOpen")
        self.btnCopy = self.findChild(QPushButton, "btnCopy")

        self.init_handler()
        self.loadHsvSpace()
        self.updateHSVPreview()


    def loadHsvSpace(self):
        self.imgHsvSpace = cv2.imread(os.path.join(os.path.dirname(__file__), "assets", "hsv_color.png"))

    def init_handler(self):
        self.sliderH.valueChanged.connect(self.onHChanged)
        self.sliderS.valueChanged.connect(self.onSChanged)
        self.sliderV.valueChanged.connect(self.onVChanged)
        self.cboxSetMode.currentTextChanged.connect(self.onCBoxModeChanged)
        self.btnOpen.clicked.connect(self.onBtnOpenClicked)
        self.btnCopy.clicked.connect(self.onBtnCopyClicked)

    def onBtnCopyClicked(self):
        self.window.updateLowerUpper(self.lowerHSV, self.upperHSV)
        self.window.addNewLogLine(f"New values set\n\tUpper: {self.upperHSV}\n\tLower: {self.lowerHSV}")
        with open('hsv.json', 'w', encoding='utf-8') as f:
            json_data = {
                "hsv":
                    {
                        "colorUpper": self.upperHSV,
                        "colorLower": self.lowerHSV
                    }

            }
            json.dump(json_data, f, ensure_ascii=False, indent=4)

    # =========== Helper ===========
    def updatePreviewHsvSpace(self):
        # refreshes the box on the bottom left in the HSV tab
        if self.imgHsvSpace is None:
            return

        frame_HSV = cv2.cvtColor(self.imgHsvSpace, cv2.COLOR_BGR2HSV)
        lower_orange = np.array(self.lowerHSV)
        upper_orange = np.array(self.upperHSV)

        frame_threshold = cv2.inRange(
            frame_HSV, lower_orange, upper_orange)

        frame_threshold = cv2.bitwise_and(self.imgHsvSpace, self.imgHsvSpace, mask=frame_threshold)
        _asQImage = QImage(
            frame_threshold.data, frame_threshold.shape[1], frame_threshold.shape[0], frame_threshold.shape[1] * 3,
            QtGui.QImage.Format_RGB888)
        _asQImage = _asQImage.rgbSwapped()
        self.previewHsvSpace.setPixmap(QPixmap.fromImage(_asQImage).scaledToWidth(self.previewMask.size().width()))

    def updateHSVPreview(self):
        prevH = generateSolidColorPixmap(
            200, 300, QColor.fromHsv(self.selectedHue, 255, 255))
        self.previewH.setPixmap(QPixmap.fromImage(prevH))

        prevS = generateSolidColorPixmap(
            200, 300, QColor.fromHsv(self.selectedHue, self.selectedSaturation, 255))
        self.previewS.setPixmap(QPixmap.fromImage(prevS))

        prevV = generateSolidColorPixmap(
            200, 300, QColor.fromHsv(self.selectedHue, self.selectedSaturation, self.selectedValue))
        self.previewV.setPixmap(QPixmap.fromImage(prevV))

        if self.cboxSetMode.currentText() == "UPPER":
            self.upperHSV = (self.selectedHue // 2,
                             self.selectedSaturation, self.selectedValue)
            self.lblUpper.setText(
                f"H {self.upperHSV[0]}; S {self.upperHSV[1]}; V {self.upperHSV[2]}")
        elif self.cboxSetMode.currentText() == "LOWER":
            self.lowerHSV = (self.selectedHue // 2,
                             self.selectedSaturation, self.selectedValue)
            self.lblLower.setText(
                f"H {self.lowerHSV[0]}; S {self.lowerHSV[1]}; V {self.lowerHSV[2]}")

        self.updateMask()
        self.updatePreviewHsvSpace()

    def updateRawImg(self, img):
        # _dsize = (self.previewRaw.size().height(),
        #           self.previewRaw.size().width())
        self.imgRaw = img
        _imgAsQImg = QImage(self.imgRaw.data, self.imgRaw.shape[1], self.imgRaw.shape[0], QImage.Format_RGB888).rgbSwapped()
        # self.imgRaw = img.scaled(200,100, QtCore.KeepAspectRatio)
        # self.imgRaw = img.scaledToHeight(self.previewMask.size().height())
        self.previewRaw.setPixmap(QPixmap.fromImage(_imgAsQImg).scaledToWidth(self.previewRaw.size().width()))

    def updateMask(self):
        if self.imgRaw is None:
            return
        frame_HSV = cv2.cvtColor(self.imgRaw, cv2.COLOR_BGR2HSV)
        lower_orange = np.array(self.lowerHSV)
        upper_orange = np.array(self.upperHSV)

        frame_threshold = cv2.inRange(
            frame_HSV, lower_orange, upper_orange)

        self.updateMaskedRaw(frame_threshold)
        frame_threshold = cv2.cvtColor(frame_threshold, cv2.COLOR_GRAY2RGB)

        _asQImage = QImage(
            frame_threshold.data, frame_threshold.shape[1], frame_threshold.shape[0], frame_threshold.shape[1] * 3,
            QtGui.QImage.Format_RGB888)
        _asQImage = _asQImage.rgbSwapped()
        self.previewMask.setPixmap(QPixmap.fromImage(_asQImage).scaledToHeight(self.previewMask.size().height()))

    def updateMaskedRaw(self, masking):
        # refreshes the box on the bottom right in the HSV tab
        if self.imgRaw is None:
            return
        frame_threshold = cv2.bitwise_and(self.imgRaw, self.imgRaw, mask=masking)
        _asQImage = QImage(
            frame_threshold.data, frame_threshold.shape[1], frame_threshold.shape[0], frame_threshold.shape[1] * 3,
            QtGui.QImage.Format_RGB888)
        _asQImage = _asQImage.rgbSwapped()
        self.previewMaskedRaw.setPixmap(
            QPixmap.fromImage(_asQImage).scaledToHeight(self.previewMaskedRaw.size().height()))

    # =========== EVENT HANDLER ===========

    def onCBoxModeChanged(self, text):
        if text == "UPPER":
            self.selectedHue = self.upperHSV[0] * 2
            self.selectedSaturation = self.upperHSV[1]
            self.selectedValue = self.upperHSV[2]
        elif text == "LOWER":
            self.selectedHue = self.lowerHSV[0] * 2
            self.selectedSaturation = self.lowerHSV[1]
            self.selectedValue = self.lowerHSV[2]

        self.sliderH.setValue(self.selectedHue)
        self.sliderS.setValue(self.selectedSaturation)
        self.sliderV.setValue(self.selectedValue)

        self.updateHSVPreview()

    def onHChanged(self):
        _v = self.selectedHue = self.sliderH.value()
        self.lblH.setText(str(f"QT5 ({_v}) | cv2 ({_v // 2})"))
        self.updateHSVPreview()

    def onSChanged(self):
        _v = self.selectedSaturation = self.sliderS.value()
        self.lblS.setText(str(_v))
        self.updateHSVPreview()

    def onVChanged(self):
        _v = self.selectedValue = self.sliderV.value()
        self.lblV.setText(str(_v))
        self.updateHSVPreview()

    @pyqtSlot(QImage)
    def setImg(self, image):
        # Video in PyQt5 in other thread:
        # https://stackoverflow.com/questions/44404349/pyqt-showing-video-stream-from-opencv
        self.imgRaw = cv2.imread(FILE_NAME)
        self.previewRaw.setPixmap(QPixmap.fromImage(image).scaledToWidth(self.previewRaw.size().width()))

    def onBtnOpenClicked(self):
        try:
            self.image_thread = self.window.video_thread
            self.image_thread.hsvImage.connect(self.setImg)
            self.image_thread.set_emit_one_pic()
            self.window.addNewLogLine(f"The image has been loaded.")
        except Exception as ex:
            self.window.addNewLogLine(f"Video stream must be running")

