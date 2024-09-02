import time
import sys
import tfmpi2c as tfmP   # Import `tfmpi2c` module v0.0.7
from tfmpi2c import *    # and also import all definitions


# - - - -  Set and Test I2C communication  - - - -
#  I2C(4) is default I2CPort for this module
#  0x10 is the default I2CAddr for TFMini-Plus
#  This function is needed only to change I2CPort
#  and/or I2CAddr, and to test those settings.
# - - - - - - - - - - - - - - - - - - - - - - - - -
#I2CPort = 0     # I2C(0), /dev/i2c-0, GPIO 0/1, pins 27/28
I2CPort = 0      # I2C(4), /dev/i2c-4, GPIO 8/9, pins 24/21
I2CAddr = 0x57  # Device address in Hex, Decimal 16
print( "I2C mode: ", end='')
if(tfmP.begin( I2CPort, I2CAddr)):
    print( "ready")
else:
    print( "not ready")
    sys.exit()   #  quit the program if I2C bus not ready
# - - - - - - - - - - - - - - - - - - - - - - - -'''

# - - - - - -  Miscellaneous commands  - - - - - - -
#      None of these are strictly necessary.
#        Many more commands are available.
# - - - - - - - - - - - - - - - - - - - - - - - - -
#
# - - Perform a system reset - - - - - - - -
print( "System reset: ", end= '')
if( tfmP.sendCommand( SYSTEM_RESET, 0)):
    print( "passed")
else:
    tfmP.printReply()
time.sleep(0.5)  # allow 500ms for reset to complete
# - - - - - - - - - - - - - - - - - - - - - - - -
#
# - - Get and Display the firmware version - - - - - - -
print( "Firmware version: ", end= '')
if( tfmP.sendCommand( OBTAIN_FIRMWARE_VERSION, 0)):
    print( tfmP.version)
else:
    tfmP.printReply()
# - - - - - - - - - - - - - - - - - - - - - - - -
#
# - - Set the data-frame rate to 20Hz - - - - - - - -
print( "Data-Frame rate: ", end= '')
if( tfmP.sendCommand( SET_FRAME_RATE, FRAME_20)):
    print( str(FRAME_20) + 'Hz')
else:
    tfmP.printReply()
# - - - - - - - - - - - - - - - - - - - - - - - -
time.sleep(0.5)     # Wait half a second.
#
# - - - - - -  miscellaneous commands ends here  - - - - - - -