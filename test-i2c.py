import time

from TFminiI2C import TFminiI2C

try:
    while True:
        sensor0 = TFminiI2C(1, 0x50)
        sensor1 = TFminiI2C(1, 0x57)
        print(sensor0.readDistance())
        print(sensor1.readDistance())
        time.sleep(0.1)

except KeyboardInterrupt:  # Ctrl+C
    print("Program interrupted")
