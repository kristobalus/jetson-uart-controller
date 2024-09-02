import smbus2
import time

# I2C address of the TFmini-I2C LiDAR sensor
LIDAR_I2C_ADDRESS = 0x50  # Default I2C address

# Register addresses
REGISTER_HIGH_BYTE = 0x01
REGISTER_LOW_BYTE = 0x02

# Initialize the I2C bus
bus = smbus2.SMBus(0)  # 1 indicates /dev/i2c-1


def read_distance():
    try:
        # Read the high and low byte from the register
        high_byte = bus.read_byte_data(LIDAR_I2C_ADDRESS, REGISTER_HIGH_BYTE)
        low_byte = bus.read_byte_data(LIDAR_I2C_ADDRESS, REGISTER_LOW_BYTE)

        # Combine the two bytes into a 16-bit value
        distance = (high_byte << 8) + low_byte

        return distance
    except Exception as e:
        print(f"Error reading distance: {e}")
        return None


if __name__ == "__main__":
    while True:
        distance = read_distance()
        if distance is not None:
            print(f"Distance: {distance} cm")
        else:
            print("Failed to read distance")
        time.sleep(1)  # Delay between readings
