import time
from smbus2 import SMBus, i2c_msg


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

# Buffer sizes
TFMP_FRAME_SIZE =  9   # Size of one data frame = 9 bytes
TFMP_COMMAND_MAX = 8   # Longest command = 8 bytes
TFMP_REPLY_SIZE =  8   # Longest command reply = 8 bytes

#
# System Error Status Condition
TFMP_READY        =  0  # no error
TFMP_SERIAL       =  1  # serial timeout
TFMP_HEADER       =  2  # no header found
TFMP_CHECKSUM     =  3  # checksum doesn't match
TFMP_TIMEOUT      =  4  # I2C timeout
TFMP_PASS         =  5  # reply from some system commands
TFMP_FAIL         =  6  #           "
TFMP_I2CREAD      =  7
TFMP_I2CWRITE     =  8  # I2C write failure
TFMP_I2CLENGTH    =  9
TFMP_WEAK         = 10  # Signal Strength ≤ 100
TFMP_STRONG       = 11  # Signal Strength saturation
TFMP_FLOOD        = 12  # Ambient Light saturation
TFMP_MEASURE      = 13


#
#  Create a proper command byte array, send the command,
#  get a response, and return the status
def sendCommand( cmnd, param):
    ''' Send command and get reply data'''

    # - - - - - - - - - - - - - - - - - - - - - - - - -
    # Step 1 - A little housekeeping
    # - - - - - - - - - - - - - - - - - - - - - - - - -
    # make data and status variables global
    global status, dist, flux, temp, version, reply
    # clear status variable of any error condition
    status = TFMP_READY;
    # - - - - - - - - - - - - - - - - - - - - - - - - -

    #  - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #  Step 1 - Build a command data array
    #  - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # From 32bit 'cmnd' integer, create a four byte array of:
    # reply length, command length, command number and a one byte parameter
    cmndData = bytearray( cmnd.to_bytes( TFMP_COMMAND_MAX, byteorder = 'little'))
    #
    replyLen = cmndData[ 0]    #  Save the first byte as reply length.
    cmndLen = cmndData[ 1]     #  Save the second byte as command length.
    cmndData[ 0] = 0x5A        #  Set the first byte to the HEADER code.
    #
    if( cmnd == SET_FRAME_RATE):    #  If the command is Set FrameRate...
        cmndData[3:2] = param.to_bytes( 2, byteorder = 'little')     #  add the 2 byte FrameRate parameter.
    elif( cmnd == SET_BAUD_RATE):   #  If the command is Set BaudRate...
        cmndData[3:3] = param.to_bytes( 3, byteorder = 'little')     #  add the 3 byte BaudRate parameter.
    #
    cmndData = cmndData[0:cmndLen]  # re-establish length of command data array
    #
    #  Create a checksum for the last byte of the array
    #  (Tests indicate the presence of the byte is
    #  necessary, but the value is irrelevant.)
    chkSum = 0
    #  Add together all bytes but the last.
    for i in range( cmndLen -1):
        chkSum += cmndData[ i]
    #  and save it as the last byte of command data.
    cmndData[ cmndLen -1] = ( chkSum & 0xFF)
    #  - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    #  - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #  Step 2 - Send the command data array to the device
    #  - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    cmndList = list(cmndData)
    bus = SMBus(0)
    bus.write_i2c_block_data(0x50, 0, cmndList)
    bus.close()
    #
    #  If the command does not expect a reply, then we're
    #  finished here. Go home.
    if( replyLen == 0):
        return True
    #  + + + + + + + + + + + + + + + + + + + + + + + + +

    #  - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #  Step 3 - Get command reply data back from the device.
    #  - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #  Give device a chance to fill its registers
    time.sleep(0.002)
    #  Read block of data into declared list 'reply'
    bus = SMBus(0, True)
    reply = bus.read_i2c_block_data(0x50, 0, replyLen)
    bus.close()

    '''
    for i in range( replyLen):
        reply[ i] = bus.read_byte( addr)
    for i in range( len(reply)):
        print( f" {reply[i]:0{2}X}", end='')
    print()
    '''

    #  - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #  Step 4 - Perform a checksum test.
    #  - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #  Declare and clear the 'chkSum' variable
    chkSum = 0
    #  Add together all bytes but the last.
    for i in range( replyLen -1):
        chkSum += reply[ i]
    #  If the low order byte does not equal the last byte...
    if( ( chkSum & 0xff) != reply[ replyLen - 1]):
        status = TFMP_CHECKSUM  #  ...then set error
        return False            #  and return 'False.'

    #  - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #  Step 5 - Interpret different command responses.
    #  - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    if( cmnd == OBTAIN_FIRMWARE_VERSION):
        version =\
            str( reply[ 5]) + '.' +\
            str( reply[ 4]) + '.' +\
            str( reply[ 3])
    else:
        if( cmnd == SYSTEM_RESET or
            cmnd == RESTORE_FACTORY_SETTINGS or
            cmnd == SAVE_SETTINGS ):
            if( reply[ 3] == 1):    #  If PASS/FAIL byte non-zero
                status = TFMP_FAIL  #  then set status to 'FAIL'
                return False        #  and return 'False'.

    #  - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #  Step 6 - Set status to 'READY' and return 'True'
    #  - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    status = TFMP_READY
    return True

# def read_sensor(address):
#     write_msg = i2c_msg.write(address, [1, 2, 7])
#     read_msg = i2c_msg.read(address, 9)
#     bus.i2c_rdwr(write_msg, read_msg)
#     data = list(read_msg)
#
#     flag = data[0]
#     dist = data[3] << 8 | data[2]
#     strength = data[5] << 8 | data[4]
#     mode = data[6]
#
#     print(address, dist)
#
#     return [flag, dist, strength, mode]


try:
    while True:
        sendCommand(OBTAIN_FIRMWARE_VERSION, 0)
        # read_sensor(0x50)
        # read_sensor(0x57)
        time.sleep(0.1)

except KeyboardInterrupt:  # Ctrl+C
    print("Program interrupted")
