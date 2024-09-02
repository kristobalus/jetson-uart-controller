import time
from smbus2 import SMBus, i2c_msg
import time

def main():
    address = 0x50
    # write Reg_H, Reg_L and Data Length to the sensor, without (!) a STOP
    # request read, specifying the sensor and 7 bytes
    write = i2c_msg.write(address, [1, 2, 7])
    read = i2c_msg.read(address, 7)

    with SMBus(0) as bus:
        bus.i2c_rdwr(write, read)
        data = list(read)
        TrigFlag = data[0]
        Dist = (data[3] << 8 | data[2])
        Strength = (data[5] << 8 | data[4])
        Mode = (data[6])

        print(Dist)
        print(Strength)
        print(Mode)

try:
    main()
except KeyboardInterrupt:  # Ctrl+C
    print("Program interrupted")
