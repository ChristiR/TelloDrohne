from djitellopy import tello
# from tello import Tello
import cv2

me = tello.Tello()
me.connect()
print(me.get_battery())

# me = Tello()
# me.send_command("command")
# print(me.send_command("battery?"))
# me.send_command("streamon")


me.streamon()

while True:
    img = me.get_frame_read().frame
    #img = cv2.resize(img,(360,240))
    cv2.imshow("Image",img)
    cv2.waitKey(1)
