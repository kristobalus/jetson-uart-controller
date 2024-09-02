import time
from smbus2 import SMBus, i2c_msg

bus = SMBus(0)

#  = = = = =  SEND A COMMAND TO THE DEVICE  = = = = = = = = = =0
#
#  - - -  Command Codes - - - - -
#  The 'sendCommand()' function expects the command
#  (cmnd) code to be in the the following format:
#  0x     00       00       00       00
#      one byte  command  command   reply
#      payload   number   length    length
OBTAIN_FIRMWARE_VERSION   = 0x00010407   # returns 3 byte firmware version
TRIGGER_DETECTION         = 0x00040400   # frame rate must be set to zero
                                         # returns a 9 byte data frame
SYSTEM_RESET              = 0x00020405   # returns a 1 byte pass/fail (0/1)
RESTORE_FACTORY_SETTINGS  = 0x00100405   #           "
SAVE_SETTINGS             = 0x00110405   # This must follow every command
                                         # that modifies volatile parameters.
                                         # Returns a 1 byte pass/fail (0/1)

SET_FRAME_RATE            = 0x00030606   # Each of these commands return
SET_BAUD_RATE             = 0x00060808   # an echo of the command
STANDARD_FORMAT_CM        = 0x01050505   #           "
PIXHAWK_FORMAT            = 0x02050505   #           "
STANDARD_FORMAT_MM        = 0x06050505   #           "
ENABLE_OUTPUT             = 0x00070505   #           "
DISABLE_OUTPUT            = 0x01070505   #           "
SET_I2C_ADDRESS           = 0x100B0505   #           "

SET_SERIAL_MODE           = 0x000A0500   # default is Serial (UART)
SET_I2C_MODE              = 0x010A0500   # set device as I2C slave

I2C_FORMAT_CM             = 0x01000500   # returns a 9 byte data frame
I2C_FORMAT_MM             = 0x06000500   #           "
#
# - - Command Parameters - - - -
BAUD_9600          = 0x002580   # UART serial baud rate
BAUD_14400         = 0x003840   # expressed in hexadecimal
BAUD_19200         = 0x004B00
BAUD_56000         = 0x00DAC0
BAUD_115200        = 0x01C200
BAUD_460800        = 0x070800
BAUD_921600        = 0x0E1000

FRAME_0            = 0x0000    # internal measurement rate
FRAME_1            = 0x0001    # expressed in hexadecimal
FRAME_2            = 0x0002
FRAME_5            = 0x0005    # set to 0x0003 in prior version
FRAME_10           = 0x000A
FRAME_20           = 0x0014
FRAME_25           = 0x0019
FRAME_50           = 0x0032
FRAME_100          = 0x0064
FRAME_125          = 0x007D
FRAME_200          = 0x00C8
FRAME_250          = 0x00FA
FRAME_500          = 0x01F4
FRAME_1000         = 0x03E8


def read_sensor(address):
    # write_msg = i2c_msg.write(address, [1, 2, 7])
    write_msg = i2c_msg.write(address, OBTAIN_FIRMWARE_VERSION)
    read_msg = i2c_msg.read(address, 3)
    bus.i2c_rdwr(write_msg, read_msg)
    data = list(read_msg)

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
