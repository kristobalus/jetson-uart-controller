from urllib.parse import urlparse

import serial # pyserial
import time
import os
import json
import paho.mqtt.client as mqtt
import logging as log

# get log level from environment variable
log_level_str = os.getenv('LOG_LEVEL', 'INFO').upper()
log_level = getattr(log, log_level_str, log.INFO)

# configure logging
log.basicConfig(
    level=log_level,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        log.StreamHandler()
    ]
)

# MQTT Configuration
mqtt_broker_url = os.getenv('MQTT_BROKER')
if not mqtt_broker_url:
    log.error("MQTT_BROKER environment variable not set or is empty")
    raise ValueError("MQTT_BROKER environment variable not set or is empty")

parsed_mqtt_broker_url = urlparse(mqtt_broker_url)
MQTT_BROKER_HOST = parsed_mqtt_broker_url.hostname
MQTT_BROKER_PORT = int(parsed_mqtt_broker_url.port)

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
topic_input = node_input[0]  # assume just one neuron expects readings
MQTT_TOPIC_DATA = f"nodes/{node_id}/input/{topic_input}"


# MQTT Callbacks
def on_connect(client, userdata, flags, rc):
    log.info("Connected to MQTT Broker with result code " + str(rc))


# MQTT Client Setup
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, 60)
# Start the MQTT client loop in a separate thread
mqtt_client.loop_start()

# LiDAR Serial Setup
serial_port = config.get('serial_port', '/dev/ttyTHS0')  # Default to '/dev/ttyTHS0' if 'dev' is not set
baud_rate = config.get('baud_rate', 115200)  # Default to '/dev/ttyTHS0' if 'dev' is not set
read_interval = int(config.get('read_interval', 0.1))  # in seconds
# Extract min and max distance values for normalization
distance_min = config.get('distance_min', 0)
distance_max = config.get('distance_max', 10000)

ser = serial.Serial(serial_port, baud_rate)


# distance normalization function
def normalize(value, min_value, max_value):
    return (value - min_value) / (max_value - min_value)


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

                    normalized_distance = normalize(distance, distance_min, distance_max)
                    data = {'distance': normalized_distance, 'strength': strength}
                    log.debug(f"lidar data: {data}")

                    mqtt_client.publish(MQTT_TOPIC_DATA, normalized_distance)

            time.sleep(read_interval)
    except Exception as err:
        log.error(f"An error occurred: {err}")
    finally:
        ser.close()


# blocking loop
main_loop(mqtt_client)
