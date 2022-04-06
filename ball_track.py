import time
import imutils
from djitellopy import tello
import cv2

me = tello.Tello()
me.connect()
print(me.get_battery())
me.streamon()
me.takeoff()
me.send_rc_control(0,0,-25,10)
print(me.get_current_state())
time.sleep(10)
print("DURCH")
#Frame größe
width = 600
height = 600
#einstellungen
framecenter = (int(width//2), int(height//2))
Abstandradius = 40
abstandaccuracy = 0.3 # genauigkeit abstand
accuracy = 0.3 #genauigkeit was noch mitte ist



#Colorcode in HSV
colorLower = (29, 86, 6)
colorUpper = (64, 255, 255)
while True:
    # Variablen
    lr = 0
    vr = 0
    hr = 0
    speed = 0
    print(me.get_current_state())
    frame = me.get_frame_read().frame
    if frame is None:
        break
    # resize the frame, blur it, and convert it to the HSV
    # color space
    frame = imutils.resize(frame, width, height)
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    #create a mask for the color you want, then perform
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
        #print(center)
        # only proceed if the radius meets a minimum size
        if radius > 5:
            # draw the circle and centroid on the frame
            cv2.circle(frame, (int(x), int(y)), int(radius),
                       (0, 255, 255), 2)
            cv2.circle(frame, center, 5, (0, 0, 255), -1)
        # show the frame to our screen
        cv2.imshow("Frame", frame)
        if center[0] > (framecenter[0]+(framecenter[0]*accuracy)):
            #ball rechts von mitte
            print("LINKS")
            lr = -10
        if center[0] < (framecenter[0]-(framecenter[0]*accuracy)):
            # ball links von mitte
            print("RECHTS")
            lr = 10
        if center[1] < (framecenter[1]-(framecenter[1]*accuracy)):
            # ball über mitte
            print("RUNTER")
            hr = 10
        if center[1] > (framecenter[1]+(framecenter[1]*accuracy)):
            # ball unter mitte
            print("HOCH")
            hr = -10
        if radius < (Abstandradius-(Abstandradius*abstandaccuracy)):
            #ball bewegt sich weg
            print("VORWÄRTS")
            vr = -10
        if radius > (Abstandradius+(Abstandradius*abstandaccuracy)):
            #ball bewegt sich auf drohne zu
            print("RÜCKWÄRTS")
            vr = 10
        speed = 10
        me.send_rc_control(lr,vr,hr,speed)
        print("links/rechts: " + str(lr) + "  vorwärts/rückwärts: " + str(vr) + "  hoch/runter: " + str(vr) + "  speed: " + str(speed))
        key = cv2.waitKey(1) & 0xFF
        # if the 'q' key is pressed, stop the loop
        if key == ord("q"):
            me.land()
            break
    else:
        print("no ball")
        #Sicherung wenn kein ball entdeckt nichts machen
me.streamoff()
cv2.destroyAllWindows()