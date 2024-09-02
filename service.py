import serial
import time
import os
import json
import paho.mqtt.client as mqtt

# MQTT Configuration
MQTT_BROKER = os.getenv('MQTT_BROKER')
MQTT_PORT = int(os.getenv('MQTT_PORT', 1883))


# Get the configuration JSON from the environment variable
config_json = os.getenv('CONFIGURATION')

# Parse the JSON to extract the serial port device name
if config_json:
    config = json.loads(config_json)
else:
    raise ValueError("CONFIGURATION environment variable not set or is empty")


node_id = config.get('node', {}).get('id')
node_input = config.get('node', {}).get('input', [])
if not node_input:
    raise ValueError("Input list is empty or not defined in the configuration.")
topic_input = node_input[0]  # Taking the first input if multiple are present
MQTT_TOPIC_DATA = f"nodes/{node_id}/input/{topic_input}"


# MQTT Callbacks
def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT Broker with result code " + str(rc))


# MQTT Client Setup
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
# Start the MQTT client loop in a separate thread
mqtt_client.loop_start()


# LiDAR Serial Setup
serial_port = config.get('serial_port', '/dev/ttyTHS0')  # Default to '/dev/ttyTHS0' if 'dev' is not set
baud_rate = config.get('baud_rate', 115200)  # Default to '/dev/ttyTHS0' if 'dev' is not set
read_interval = int(config.get('read_interval', 0.1))  # in seconds
ser = serial.Serial(serial_port, baud_rate)


# LiDAR data reading and publishing
def main_loop(mqtt_client):
    try:
        while True:
            count = ser.in_waiting
            if count > 8:
                recv = ser.read(9)
                ser.reset_input_buffer()
                if recv[0] == 0x59 and recv[1] == 0x59:
                    distance = recv[2] + recv[3] * 256
                    strength = recv[4] + recv[5] * 256
                    data = {'distance': distance, 'strength': strength}
                    print(f"Publishing: {data}")
                    mqtt_client.publish(MQTT_TOPIC_DATA, str(data))
            time.sleep(read_interval)
    except Exception as err:
        print(f"An error occurred: {err}")
    finally:
        ser.close()


# blocking loop
main_loop(mqtt_client)
