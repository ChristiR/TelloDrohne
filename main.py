# Schreibe hier Deinen Code :-)
from tello import Tello
from tkinter import *
from datetime import datetime
import time
import sys

tello = Tello();
tello.send_command("command");
# tello.send_command("takeoff");
# tello.send_command("stop");
# tello.send_command("land");
#tello.send_command("emergency");
tello.send_command("streamon");
#tello.send_command("streamoff");

root = Tk()
root.geometry("800x450+100+50")
root.title('Tello Drone Control')

frame0 = Frame(root,width=800, height=10)
frame_scale = Frame(root)

frame12= Frame(root)
frame1 = Frame(frame12)
frame2 = Frame(frame12)

frame_flip = Frame(root)


button_emergency = Button(frame0, text='emergency', width=10, command=lambda: tello.send_command(
    'emergency')).grid(row=0, column=0, padx=90, pady=10)

frame0.pack()
frame_scale.pack( pady=20)
frame1.grid(row=0, column=0,padx=80)
frame2.grid(row=0, column=1,padx=80)
frame12.pack(pady=0)
frame_flip.pack(pady=30)

