from urllib.parse import urlparse

import serial  # pyserial
import time
import os
import json
import paho.mqtt.client as mqtt
import logging as log
from test_streamer import start_test_streamer

# configure logging
# get log level from environment variable
log_level = os.getenv('LOG_LEVEL', 'INFO')
log.basicConfig(
    level=getattr(log, log_level.upper(), log.INFO),
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
config_json = os.getenv("CONFIGURATION")
if config_json:
    config = json.loads(config_json)
else:
    raise ValueError("CONFIGURATION environment variable not set or is empty")


# MQTT Callbacks
def on_connect(client, userdata, flags, rc):
    log.info("MQTT connected to broker with result code: " + str(rc))


# MQTT Client Setup
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, 60)
mqtt_client.loop_start()  # start the MQTT client loop in a separate thread

# LiDAR Serial Setup
serial_port = config.get('serial_port', '/dev/tty-test-out')
baud_rate = int(config.get('baud_rate', 115200))
read_interval = float(config.get('read_interval_secs', 0.01))  # in seconds
# extract min and max distance values for normalization
distance_min = int(config.get('distance_min_cm', 0))
distance_max = int(config.get('distance_max_cm', 10000))
topic = config.get('topic')

log.info("configuration %s", { "config": config })
log.info(f"serial_port {serial_port}")

if serial_port == "/dev/tty-test-out":
    start_test_streamer()
    log.debug("test data stream started on /dev/tty-test-in")

serial_reader = serial.Serial(serial_port, baud_rate)


# distance normalization function
def normalize(value, min_value, max_value):
    return (value - min_value) / (max_value - min_value)


# LiDAR data reading and publishing
def main_loop(mqtt_client):
    try:
        while True:
            count = serial_reader.in_waiting
            if count > 8:
                recv = serial_reader.read(9)
                serial_reader.reset_input_buffer()
                if recv[0] == 0x59 and recv[1] == 0x59:
                    distance = recv[2] + recv[3] * 256
                    strength = recv[4] + recv[5] * 256
                    normalized_distance = normalize(distance, distance_min, distance_max)

                    log.debug("lidar data: %s", {"distance": distance,
                                                 "strength": strength,
                                                 "normalized_distance": normalized_distance})

                    mqtt_client.publish(topic, normalized_distance)

            time.sleep(read_interval)
    except Exception as err:
        log.error(f"An error occurred: {err}")
    finally:
        serial_reader.close()


# blocking loop
main_loop(mqtt_client)
