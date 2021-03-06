#!/usr/bin/python3

"""
Sometimes the grower sensor csv file gets corrupted and reads 0 bytes. We want
to backup this file but only if the size of the file is greater than
0 bytes
"""
from datetime import datetime
import logging
import os
import time


SENSOR_PATH = "/home/pi/indoor_ag/data/sensors/saffron_grow_sensors.csv"
SENSOR_PATH_BACKUP = "/home/pi/indoor_ag/data/sensors/saffron_grow_sensors_backup.csv"
BACKUP_ERROR_LOG_PATH = "/home/pi/indoor_ag/logs/backup_file_error_log.txt"

logging.basicConfig(
    filename=BACKUP_ERROR_LOG_PATH,
    filemode="w",
    format="%(asctime)s - %(message)s",
)


while True:
    # Make a backup twice an hour
    now_dt = datetime.now()
    now_str = now_dt.strftime("%m%d%Y_%H%M")
    current_file_size = os.stat(SENSOR_PATH).st_size
    if current_file_size < 1:
        os.system("sudo rm {}".format(SENSOR_PATH))
        os.system("mv {} {}_{}".format(SENSOR_PATH_BACKUP, SENSOR_PATH_BACKUP, now_str))
        logging.error("Corrupt sensor file", exc_info=True)
        os.system("sudo shutdown -r now")
    else:
        os.system("cp {} {}".format(SENSOR_PATH, SENSOR_PATH_BACKUP))
    time.sleep(600)
