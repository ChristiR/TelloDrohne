# import cv2
#import numpy as np
# from djitellopy import tello
#
# me = tello.Tello()
# me.connect()
# me.streamon()
# me.takeoff()
# me. send_rc_control(0,0,-25,0)
#time.sleep(2.2)
#
# w,h = 360,240
# fbRange = [6200, 6800]
# pid = [0.4, 0.4, 0]
# pError = 0
#
# def findBall(img):
#     ballCascade = cv2.CasscadeClassifier("Rsources/*.xml")
#     imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#     balls = ballCascade.detectMultiScale(imgGray, 1.2, 8)
#     myBallsListC = []
#     myBallsListArea = []
#     for (x,y,w,h) in balls:
#         cv2.rectangle(img, (x,y),(x+w,y+h),(0,0,255),2)
#         cx = x + w // 2
#         cy = y + h // 2
#         area = w * h
#         cv2.circle(img,(cx,cy),5,(0,255,0),cv2.FILLED)
#         myBallsListC.append([cx,cy])
#         myBallsListArea.append(area)
#         if len(myBallsListArea) !=0:
#             i = myBallsListArea(max(myBallsListArea))
#             return img, [myBallsListC[i],myBallsListArea[i]]
#         else:
#             return img,[[0,0],0]
#
# def trackBall(me, info, w, pid, pError):
#     area = info[1]
#     x,y = info[0]
#     fb= 0
#     error = x-w//2
#     speed = pid[0]*error + pid[1] * (error-pError)
#     speed = int(np.clip(speed, -100, 100))
#
#     if area > fbRange[0] and area < fbRange[1]:
#         fb=0
#     elif area > fbRange[1]:
#         fb = -20
#     elif area<fbRange[0] and area != 0:
#         fb = 20
#     if x == 0:
#         speed = 0
#         error = 0
#         me.send_rc_control(0,fb,0,speed)
#         return error
#
#
# #cap = cv2.VideoCapture(1)
# while True:
#     #_, img = cap.read()
#     img = me.get_frame_read().frame
#     img = cv2.resize(img, (w,h))
#     img, info = findBall(img)
#     pError = trackBall(me, info, w, pid, pError)
#     print("Area", info[1], "Center", info[0])
#     cv2.imshow("Output",img)
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         me.land()
#         break