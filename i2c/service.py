from urllib.parse import urlparse
from smbus2 import SMBus, i2c_msg

import time
import os
import json
import paho.mqtt.client as mqtt
import logging as log
import random
from unittest.mock import MagicMock

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
i2c_bus = config.get('i2c_bus', 1)
i2c_address = int(config.get('i2c_address', "0x10"), 16)
baud_rate = int(config.get('baud_rate', 115200))
read_interval_secs = float(config.get('read_interval_secs', 0.01))  # in seconds
distance_min = int(config.get('distance_min_cm', 0))
distance_max = int(config.get('distance_max_cm', 10000))
use_fake_device = bool(config.get('use_fake_device', False))
topic = config.get('topic')

if topic is None:
    raise Exception("Should have topic defined")

i2c_read_msg = None
i2c_write_msg = None

if use_fake_device:
    log.debug("using fake device")


    def randomizer(arg1, arg2):
        global i2c_read_msg
        i2c_read_msg = [
            0x00,  # header
            0x00,  # header
            0x12,  # distance high
            0x34,  # distance low
            0x00,  # strength high
            0x56,  # strength low
            0x01,  # mode byte
            0x00,  # ??
            0x00  # ??
        ]
        # Randomize distance (2 bytes)
        distance = random.randint(0, distance_max)
        i2c_read_msg[2] = distance & 0xFF  # LSB
        i2c_read_msg[3] = (distance >> 8) & 0xFF  # MSB
        # Randomize strength (2 bytes)
        strength = random.randint(0, 0xFFFF)
        i2c_read_msg[4] = strength & 0xFF  # LSB
        i2c_read_msg[5] = (strength >> 8) & 0xFF  # MSB

    bus = MagicMock()
    i2c_write_msg = [0x5A, 0x05, 0x00, 0x01, 0x60]
    i2c_read_msg = [0x00, 0x00, 0x12, 0x34, 0x00, 0x56, 0x01, 0x00, 0x00]
    bus.i2c_rdwr = MagicMock(return_value=i2c_read_msg, side_effect=randomizer)
else:
    bus = SMBus(i2c_bus)
    i2c_write_msg = i2c_msg.write(i2c_address, [0x5A, 0x05, 0x00, 0x01, 0x60])
    i2c_read_msg = i2c_msg.read(i2c_address, 9)


# distance normalization function
def normalize(value, min_value, max_value):
    return (value - min_value) / (max_value - min_value)


# LiDAR data reading and publishing
def main_loop(mqtt_client):
    try:
        while True:
            bus.i2c_rdwr(i2c_write_msg, i2c_read_msg)
            data = list(i2c_read_msg)
            distance = (data[3] << 8 | data[2])
            strength = data[5] << 8 | data[4]
            mode = data[6]

            normalized_distance = normalize(distance, distance_min, distance_max)

            log.debug("lidar data: %s", {"distance": distance,
                                         "strength": strength,
                                         "normalized_distance": normalized_distance,
                                         "mode": mode})

            mqtt_client.publish(topic, json.dumps({"signal": normalized_distance}))

            time.sleep(read_interval_secs)
    except Exception as err:
        log.error(f"An error occurred: {err}")
    finally:
        bus.close()


# blocking loop
main_loop(mqtt_client)
