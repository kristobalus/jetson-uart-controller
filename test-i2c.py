from smbus2 import SMBus, i2c_msg
import time

# I2C address of the TFmini Plus (default is 0x10)
I2C_ADDRESS = 0x50

# Initialize the I2C bus (use the correct bus number, e.g., 1 for Raspberry Pi)
bus = SMBus(0)

# Command to obtain the firmware version
command = [0x5A, 0x04, 0x01, 0x5F]

# Send the command
write_msg = i2c_msg.write(I2C_ADDRESS, command)
bus.i2c_rdwr(write_msg)

# Wait briefly to allow the device to respond
time.sleep(0.1)

# Read the response (assume a response length of 7 bytes for firmware version)
read_msg = i2c_msg.read(I2C_ADDRESS, 7)
bus.i2c_rdwr(read_msg)

# Close the I2C bus
bus.close()

# Convert the response to a list of integers
response = list(read_msg)

# Print the response in hexadecimal format
print("Response:", ''.join(f'{byte:02X}' for byte in response))
