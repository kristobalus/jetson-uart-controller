## proof of concept

from smbus2 import SMBus, i2c_msg
import time

address = 0x50

# write Reg_H, Reg_L and Data Length to the sensor, without (!) a STOP
# request read, specifying the sensor and 7 bytes

write = i2c_msg.write(address, [0x05, 0x00, 0x01, 0x60])
read = i2c_msg.read(address, 9)

with SMBus(0) as bus:
    start = time.time()
    bus.i2c_rdwr(write, read)
    data = list(read)

    print(data)
    print(data[0])
    print(data[2] << 8 | data[1])
    print(data[3])

    # TrigFlag = data[0]
    # Dist = ((data[3] << 8 | data[2]))
    # Strength = ((data[5] << 8 | data[4]))
    # Mode = (data[6])

    # print(Dist)
    # print(Strength)
    # print(Mode)