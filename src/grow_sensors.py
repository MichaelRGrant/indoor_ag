#!/usr/bin/python3
import grp
import logging
import os
import pwd
import sys
import time

import adafruit_ads1x15.ads1115 as ADS
import adafruit_bme680 as BME
import adafruit_ccs811 as CCS
import adafruit_htu21d as HTU
import adafruit_sht31d as SHT
import adafruit_tca9548a as TCA
import adafruit_tsl2561 as TSL
import board
import busio
from adafruit_ads1x15.analog_in import AnalogIn
import pandas as pd

sys.path.append(".")
# import ds18b20 as reservoir_temp
from soil_moisture import get_soil_moisture

# os.path.join does not work on the pi, it always
# reverts to the top-level directory: /
SENSOR_PATH = "/home/pi/indoor_ag/data/sensors/saffron_grow_sensors_.csv"
LOG_PATH = "/home/pi/indoor_ag/logs/error_log.txt"

uid = pwd.getpwnam("pi").pw_uid
gid = grp.getgrnam("pi").gr_gid

# check if PATH exists and if not create empty dataframe
if os.path.exists(SENSOR_PATH):
    sensor_df = pd.read_csv(SENSOR_PATH)
# Because this python file gets started up at boot on the pi,
# it runs as root so the ownership of files that get created
# automatically need to be changed to `pi` for write privileges.
else:
    sensor_df = pd.DataFrame()
    open(SENSOR_PATH, "w+").close()
    os.chown(SENSOR_PATH, uid, gid)

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

# initialize multiplexer board
tca_multi = TCA.TCA9548A(i2c)

# initialize saffron_grow_sensors
# tca_multi[1] = ADS1115, bme680, ccs811
ads1115 = ADS.ADS1115(tca_multi[1])
bme680_1 = BME.Adafruit_BME680_I2C(tca_multi[1])
ccs811 = CCS.CCS811(tca_multi[1])
# Analog channel 0 - soil moisture
# chan0 = AnalogIn(ads1115, ADS.P0)
chan1 = AnalogIn(ads1115, ADS.P1)
chan2 = AnalogIn(ads1115, ADS.P2)

# # tca_multi[7] = htu21d-f
# htu21d = HTU.HTU21D(tca_multi[7])
#
# # tca_multi[6]
# tsl2561 = TSL.TSL2561(test_multi[6])
# bme680_6 = BME.Adafruit_BME680_I2C(tca_multi[6])
#
# # tca_multi[5]
# sht31d = SHT.SHT31D(test_multi[5])


while True:
    try:
        now = pd.to_datetime(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        tz_offset = -time.timezone / 3600

        # #----------
        # # TOP RACK
        # # htu21d: temp/rh
        # temp_c_top_rack = htu21d.temperature
        # rh_top_rack = htu21d.relative_humidity
        # #----------
        # # MIDDLE RACK
        # # tsl2561 light sensor
        # if tsl2561.lux is not None:
        #     lux_middle_rack = round(tsl2561.lux, 1)
        # else:
        #     lux_middle_rack = tsl2561.lux
        # ir_middle_rack = tsl2561.infrared
        # broadband_middle_rack = tsl2561.broadband
        # # bme680 gas, temp, pressure, humidity sensor
        # temp_c_middle_rack = round(bme680_6.temperature, 1)
        # rh_middle_rack = round(bme680_6.humidity, 1)
        # pressure_middle_rack = round(bme680_6.pressure, 3)
        # gas_middle_rack = round(bme680_6.gas, 1)
        # #----------
        # # BOTTOM RACK
        # # sht31D temp and humidity sensor
        # temp_c_bottom_rack = round(sht.temperature, 1)
        # rh_bottom_rack = round(sht.relative_humidity, 1)

        # Room environment
        temp_c_room = round(bme680_1.temperature, 1)
        temp_f_room = round((9/5) * temp_c_room + 32, 1)
        rh_room = round(bme680_1.humidity, 1)
        pressure_room = round(bme680_1.pressure, 3)
        gas_room = round(bme680_1.gas, 1)

        # coir_vwc = round(get_soil_moisture(chan0.voltage), 2)
        coir50_vwc = round(get_soil_moisture(chan1.voltage), 2)
        rockwool_vwc = round(get_soil_moisture(chan2.voltage), 2)

        # This sensor can malfunction and throw and error, so
        # this try/except block catches any errors, waits 1 minute
        # and starts the loop over again.
        try:
            eqco2_room = ccs811.eco2
            tvoc_room = ccs811.tvoc
        except:
            time.sleep(60)
            continue

        # # resevior temperature
        # resevior_temp_c, resevior_temp_f = resevior_temp.read_temp()

        tmp_df = pd.DataFrame(
            {
                "time": now,
                "offset_from_utc": tz_offset,
                # "temp_c_top_rack": temp_c_top_rack,
                # "rh_top_rack": rh_top_rack,
                # "lux_middle_rack": lux_middle_rack,
                # "ir_middle_rack": ir_middle_rack,
                # "broadband_middle_rack": broadband_middle_rack,
                # "temp_c_middle_rack": temp_c_middle_rack,
                # "rh_middle_rack": rh_middle_rack,
                # "pressure_middle_rack": pressure_middle_rack,
                # "gas_middle_rack": gas_middle_rack,
                # "temp_c_bottom_rack": temp_c_bottom_rack,
                # "rh_bottom_rack": rh_bottom_rack,
                # "resevior_temp_c": resevior_temp_c,
                "temp_c_room": temp_c_room,
                "temp_f_room": temp_f_room,
                "rh_room": rh_room,
                "pressure_room": pressure_room,
                "gas_room": gas_room,
                "total_voc_room": tvoc_room,
                "co2_room": eqco2_room,
                # "coir_vwc": coir_vwc,
                "coir50_vwc": coir50_vwc,
                "rockwool_vwc": rockwool_vwc,
            },
            index=[0],
        ).round(1)
        sensor_df = sensor_df.append(tmp_df)
        sensor_df.to_csv(SENSOR_PATH, index=False)
        time.sleep(600)  # 10 minutes
    except Exception as e:
        print(e)
        logging.error("Exception occurred", exc_info=True)