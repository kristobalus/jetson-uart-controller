## proof of concept

from smbus2 import SMBus, i2c_msg
import time


bus = SMBus(0)
address = 0x57

# write Reg_H, Reg_L and Data Length to the sensor, without (!) a STOP
# request read, specifying the sensor and 7 bytes

OBTAIN_FIRMWARE = [0x04, 0x01, 0x5F]
READ_TRIGGER = [0x04, 0x04,  0x62]
READ_DIST_CM = [0x05, 0x00, 0x01, 0x60]
READ_DIST_MM = [0x05, 0x00, 0x06, 0x65]
write = i2c_msg.write(address, READ_DIST_CM)
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