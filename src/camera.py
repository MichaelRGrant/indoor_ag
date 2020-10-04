#!/usr/bin/env python3
import grp
import os
import pwd
from datetime import datetime

from picamera import PiCamera
from time import sleep

IMAGE_DIR = "/home/pi/indoor_ag/data/images"

uid = pwd.getpwnam("pi").pw_uid
gid = grp.getgrnam("pi").gr_gid

if not os.path.exists(IMAGE_DIR):
    os.mkdir(IMAGE_DIR)
    os.chown(IMAGE_DIR, uid, gid)


camera = PiCamera()
camera.resolution = (1296, 972)
camera.framerate = 15
while True:
    now_dt = datetime.now()
    if now_dt.hour in [20, 22, 0, 2, 4, 6, 8]:  # Take picture when clock hits 8 pm
        camera.start_preview()
        # camera needs a few seconds to warm up
        sleep(5)
        now_str = now_dt.strftime("%m%d%Y_%H%M")
        camera.capture(os.path.join(IMAGE_DIR, "saffron_{}.jpg".format(now_str)))
        camera.stop_preview()
        sleep(4000)  # just over 1 hour so the clock will be past the 8 pm conditional
