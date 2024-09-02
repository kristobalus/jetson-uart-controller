## proof of concept

from smbus2 import SMBus, i2c_msg
import time


bus = SMBus(1)
address = 0x10

write = i2c_msg.write(address, [5, 0, 1, 6])
read = i2c_msg.read(address, 9)


while True:
    start = time.time()
    bus.i2c_rdwr(write, read)
    data = list(read)
    print(data)
    dist = (data[3] << 8 | data[2])
    strength = data[5] << 8 | data[4]
    mode = data[6]
    print(dist, strength, mode)
    time.sleep(1)