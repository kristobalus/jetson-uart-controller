## proof of concept

from smbus2 import SMBus, i2c_msg
import time

address = 0x50

# write Reg_H, Reg_L and Data Length to the sensor, without (!) a STOP
# request read, specifying the sensor and 7 bytes

write = i2c_msg.write(address, [1, 4, 7])
read = i2c_msg.read(address, 3)

with SMBus(0) as bus:
    start = time.time()
    bus.i2c_rdwr(write, read)
    data = list(read)

    print(data)

    TrigFlag = data[0]
    Dist = ((data[3] << 8 | data[2]))
    Strength = ((data[5] << 8 | data[4]))
    Mode = (data[6])

    print(Dist)
    print(Strength)
    print(Mode)