#!/usr/bin/python3

"""
Sometimes the grower sensor csv file gets corrupted and reads 0 bytes. We want
to backup this file but only if the size of the file is greater than
0 bytes
"""

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
    current_file_size = os.stat(SENSOR_PATH).st_size
    if current_file_size < 1:
        logging.error("Exception occurred", exc_info=True)
    else:
        os.system("cp {} {}".format(SENSOR_PATH, SENSOR_PATH_BACKUP))
    time.sleep(600)
