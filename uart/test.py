# -*- coding: utf-8 -*
import serial

ser = serial.Serial("/dev/ttyTHS0", 115200)


def main():
    while True:
        #time.sleep(0.1)
        count = ser.in_waiting
        if count > 8:
            recv = ser.read(9)
            ser.reset_input_buffer()
            # type(recv), 'bytes' in python3(recv[0] = 89)
            # type(recv[0]), 'int' in python3
            if recv[0] == 0x59 and recv[1] == 0x59:  #python3
                distance = recv[2] + recv[3] * 256
                strength = recv[4] + recv[5] * 256
                print('(', distance, ',', strength, ')')
                ser.reset_input_buffer()

try:
    if not ser.is_open:
        ser.open()
    main()
except KeyboardInterrupt:  # Ctrl+C
    ser.close()
