import time
from tfmini_i2c import TFminiI2C


def main():
    sensor1 = TFminiI2C(0, 0x50)
    sensor2 = TFminiI2C(0, 0x57)
    while True:
        distance1 = sensor1.read_distance()
        distance2 = sensor2.read_distance()
        data1 = sensor1.read_all()
        data2 = sensor2.read_all()
        print(data1)
        print(data2)
        print("--------")
        time.sleep(1)


try:
    main()
except KeyboardInterrupt:  # Ctrl+C
    print("Program interrupted")
