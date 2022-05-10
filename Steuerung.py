import time
import imutils
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel
from djitellopy import tello
import cv2

#Frame größe
width = 600
height = 600
#einstellungen
framecenter = (int(width//2), int(height//2))
Abstandradius = 40
abstandaccuracy = 0.3 # genauigkeit abstand
accuracy = 0.3 #genauigkeit was noch mitte ist

#Colorcode in HSV
colorLower = (27, 80, 182)
colorUpper = (31, 184, 255)

def startstream(frame):
    # resize the frame, blur it, and convert it to the HSV
    # color space
    frame = imutils.resize(frame, width, height)
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    # create a mask for the color you want, then perform
    # a series of dilations and erosions to remove any small
    # blobs left in the mask
    mask = cv2.inRange(hsv, colorLower, colorUpper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    center = None
    # only proceed if at least one contour was found
    if len(cnts) > 0:
        # find the largest contour in the mask, then use
        # it to compute the minimum enclosing circle and
        # centroid
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        # only proceed if the radius meets a minimum size
        if radius > 5:
            # draw the circle and centroid on the frame
            cv2.circle(frame, (int(x), int(y)), int(radius),
                       (0, 255, 255), 2)
            cv2.circle(frame, center, 5, (0, 0, 255), -1)
        # show the frame to our screen
        #trackball(me, center, radius)
        #cv2.imshow("Frame", frame)
        # label = QLabel(self)
        # pixmap = QPixmap(frame)
        # label.setPixmap(pixmap)
    return frame
