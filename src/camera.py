#!/usr/bin/env python3
import os
from datetime import datetime

from picamera import PiCamera
from time import sleep

IMAGE_DIR = "/home/pi/indoor_ag/images"
if not os.path.exists(IMAGE_DIR):
    os.mkdir(IMAGE_DIR)

camera = PiCamera()
camera.resolution = (1296, 972)
camera.framerate = 15
while True:
    now_dt = datetime.now()
    if now_dt.hour == 20:
        camera.start_preview()
        sleep(5)
        now_str = now_dt.strftime("%m%d%Y_%H%M")
        camera.capture(os.path.join(IMAGE_DIR, "saffron_{}.jpg".format(now_str)))
        camera.stop_preview()
        sleep(4000) # just over 1 hour
