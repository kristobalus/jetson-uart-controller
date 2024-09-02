from smbus2 import smbus2, i2c_msg
import time
from tfmini_i2c import TFminiI2C

bus = smbus2.SMBus()  # or bus = smbus2.SMBus(1) e.g 1 for Raspberry Pie
bus.open(0)

# I2C address of the device
address = 0x50 # replace with your device's I2C address


def main():
    sensor = TFminiI2C(1, 0x10)
    while True:
        distance=sensor.read_distance()
        print(f"distance={distance}")
        time.sleep(0.1)


try:
    main()
except KeyboardInterrupt:  # Ctrl+C
    print("Program interrupted")
finally:
    bus.close()
