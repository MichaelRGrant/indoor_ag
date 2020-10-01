#!/usr/bin/python3
"""
This script reads the sensor dataframe and prints the data
to an LCD display hooked up to the RPi.

Author: Michael Grant
"""

import grp
import logging
import os
import pwd
import sys
import time

import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import adafruit_bme680 as BME
import adafruit_ccs811 as CCS
import adafruit_character_lcd.character_lcd as characterlcd
import adafruit_tca9548a as TCA
import board
import busio
import digitalio
import numpy as np

sys.path.append(".")
from soil_moisture import get_soil_moisture

# time.sleep(60)

LOG_PATH = "/home/pi/indoor_ag/logs/print_to_display_error_log.txt"

uid = pwd.getpwnam("pi").pw_uid
gid = grp.getgrnam("pi").gr_gid

if not os.path.exists(LOG_PATH):
    open(LOG_PATH, "w+").close()
    os.chown(LOG_PATH, uid, gid)

# initialize i2c
i2c = busio.I2C(board.SCL, board.SDA)
logging.basicConfig(
    filename=LOG_PATH,
    filemode="w",
    format="%(asctime)s - %(message)s",
)

# initialize lcd
lcd_rs = digitalio.DigitalInOut(board.D26)
lcd_en = digitalio.DigitalInOut(board.D19)
lcd_d7 = digitalio.DigitalInOut(board.D27)
lcd_d6 = digitalio.DigitalInOut(board.D22)
lcd_d5 = digitalio.DigitalInOut(board.D24)
lcd_d4 = digitalio.DigitalInOut(board.D25)
lcd_columns = 20
lcd_rows = 4
lcd = characterlcd.Character_LCD_Mono(
    lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7, lcd_columns, lcd_rows
)

# initialize multiplexer board
tca_multi = TCA.TCA9548A(i2c)

# initialize saffron_grow_sensors
# tca_multi[1] = ADS1115, bme680, ccs811
ads1115 = ADS.ADS1115(tca_multi[1])
bme680_1 = BME.Adafruit_BME680_I2C(tca_multi[1])
ccs811 = CCS.CCS811(tca_multi[1])
chan = AnalogIn(ads1115, ADS.P0)

while True:
    try:
        lcd.clear()
        temp_c_room = round(bme680_1.temperature, 1)
        rh_room = round(bme680_1.humidity, 1)
        soil_moisture = round(get_soil_moisture(chan.voltage), 2)

        # This sensor can malfunction and throw and error, so
        # this try/except block catches any errors, waits 1 minute
        # and starts the loop over again.
        try:
            eqco2_room = ccs811.eco2
        except:
            eqco2_room = np.nan

        lcd.message = "{temp}C | {rh}%\n{co2} ppm CO2\n" \
                      "{soil_moisture} VWC".format(
            temp=temp_c_room,
            rh=rh_room,
            co2=eqco2_room,
            soil_moisture=soil_moisture
        )
        time.sleep(5)

    except Exception as e:
        logging.error("Exception occurred", exc_info=True)
