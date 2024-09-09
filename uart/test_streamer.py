
import serial  # pyserial
import threading
import random
import subprocess
import time


def do_test_stream():
    print("start test streamer")

    serial_writer = serial.Serial('/dev/tty-test-in', 115200)
    serial_writer.reset_output_buffer()

    # Range of values for distance and strength
    distance_min = 4
    distance_max = 12000
    strength_min = 100
    strength_max = 1000

    print(f"Test stream started")

    try:
        while True:
            # random data to send
            distance = random.randint(distance_min, distance_max)
            strength = random.randint(strength_min, strength_max)

            # prepare the message
            send_buffer = bytearray(9)
            send_buffer[0] = 0x59  # start byte 1
            send_buffer[1] = 0x59  # start byte 2
            send_buffer[2] = distance & 0xFF  # low byte of distance
            send_buffer[3] = (distance >> 8) & 0xFF  # high byte of distance
            send_buffer[4] = strength & 0xFF  # low byte of strength
            send_buffer[5] = (strength >> 8) & 0xFF  # high byte of strength
            send_buffer[6] = 0  # placeholder for additional data
            send_buffer[7] = 0  # placeholder for additional data
            send_buffer[8] = 0  # placeholder for checksum or other data

            serial_writer.write(send_buffer)  # send the prepared buffer
            time.sleep(1)  # add delay to avoid flooding the port
    except Exception as e:
        print(f"Error while writing to serial port: {e}")
    finally:
        serial_writer.close()


def do_socat():
    command = "socat PTY,link=/dev/tty-test-in,raw,echo=0 PTY,link=/dev/tty-test-out,raw,echo=0"
    subprocess.run(command, shell=True, check=True)

def start_test_streamer():
    socat_thread = threading.Thread(target=do_socat)
    socat_thread.start()

    time.sleep(5)

    serial_thread = threading.Thread(target=do_test_stream)
    serial_thread.start()

    print("socat sockets created")



