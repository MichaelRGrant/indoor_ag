#!/usr/bin/python3
import os
import time


PATH = "/home/pi/indoor_ag/data/sensors/saffron_grow_sensors.csv"

current_file_size = os.stat(PATH).st_size

while True:
    time.sleep(600)
    if current_file_size == os.stat(PATH).st_size:
        os.system("sudo shutdown -r now")
    else:
        current_file_size = os.stat(PATH).st_size
