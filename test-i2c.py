import time
from smbus2 import SMBus, i2c_msg

bus = SMBus(0)


def read_sensor(address):
    # write_msg = i2c_msg.write(address, [1, 2, 7])
    # read_msg = i2c_msg.read(address, 7)
    # bus.i2c_rdwr(write_msg, read_msg)
    # data = list(read_msg)

    data = bus.read_i2c_block_data(address, 0, 9)

    flag = data[0]
    dist = data[3] << 8 | data[2]
    strength = data[5] << 8 | data[4]
    mode = data[6]

    print(address, dist)

    return [flag, dist, strength, mode]


try:
    while True:
        read_sensor(0x50)
        read_sensor(0x57)
        time.sleep(0.1)

except KeyboardInterrupt:  # Ctrl+C
    print("Program interrupted")
