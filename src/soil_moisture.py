# import board
# import busio
# import adafruit_ads1x15.ads1115 as ADS
# from adafruit_ads1x15.analog_in import AnalogIn
#
# i2c = busio.I2C(board.SCL, board.SDA)
# ads = ADS.ADS1115(i2c)
# chan = AnalogIn(ads, ADS.P0)


# def get_soil_moisture(voltage):
#     return convert_voltage(voltage)


def get_soil_moisture(voltage):
    if voltage <= 1.1:
        vwc = 10 * voltage - 1
    elif 1.1 < voltage <= 1.3:
        vwc = 25 * voltage - 17.5
    elif 1.3 < voltage <= 1.82:
        vwc = 48.08 * voltage - 47.5
    elif 1.82 < voltage <= 2.2:
        vwc = 26.32 * voltage - 7.89
    else:
        vwc = 62.5 * voltage - 87.5
    return vwc


# logging.basicConfig(filename='error_log_worm_vwc.txt',
#                     filemode='w',
#                     format='%(asctime)s - %(message)s')



# if os.path.isfile(PATH):
#     df = pd.read_csv(PATH)
# else:
#     df = pd.DataFrame()

# while True:
#     try:
#         now = pd.to_datetime(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
#         tz_offset = -time.timezone / 3600
#
#         vwc = convert_voltage(chan.voltage)
#
#         df = df.append(pd.DataFrame({'time': now, 'offset_from_utc': tz_offset, 'worm_bin_moisture': vwc},
#                        index=['time']))
#         df.reset_index(drop=True, inplace=True)
#         df.to_csv(PATH, index=False)
#         time.sleep(600)
#
#     except Exception as e:
#         logging.error('Exception occurred', exc_info=True)
