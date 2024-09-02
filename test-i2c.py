from smbus2 import smbus2, i2c_msg
import time

bus = smbus2.SMBus()  # or bus = smbus2.SMBus(1) e.g 1 for Raspberry Pie
bus.open(0)

# I2C address of the device
address = 0x50 # replace with your device's I2C address


def read_data():
    try:
        # Read 8 bytes from the device
        # data = bus.read_i2c_block_data(address, 0, 9)
        write = i2c_msg.write(address, [1, 2, 7])
        read = i2c_msg.read(address, 7)
        bus.i2c_rdwr(write, read)
        data = list(read)
        trig_flag = data[0]
        dist = (data[3] << 8 | data[2])
        strength = (data[5] << 8 | data[4])
        mode = (data[6])
        print(f"trig_flag={trig_flag}, dist={dist}, strength={strength}, mode={mode}")
        return data
    except IOError as e:
        print(f"Error reading from I2C device: {e}")
        return None


def main():
    while True:
        read_data()
        # if data:
        #     if data[0] == 0x59 and data[1] == 0x59:  # Check header
        #         distance = data[2] + data[3] * 256
        #         strength = data[4] + data[5] * 256
        #         print('(', distance, ',', strength, ')')
        time.sleep(0.1)


try:
    main()
except KeyboardInterrupt:  # Ctrl+C
    print("Program interrupted")
finally:
    bus.close()
