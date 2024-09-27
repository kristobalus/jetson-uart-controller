
import paho.mqtt.client as mqtt
import logging as log


# configure logging
# get log level from environment variable
log.basicConfig(
    level=log.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        log.StreamHandler()
    ]
)


# MQTT event handlers
def on_connect(client, userdata, flags, rc):
    log.info("MQTT connected with result code " + str(rc))

    client.subscribe("neurons/#")
    log.info(f"MQTT subscribed to neurons/#")


def on_message(client, userdata, msg):
    log.debug("MQTT message received on topic " + msg.topic + ": " + str(msg.payload.decode()))


# MQTT Client Setup
mqtt_client = mqtt.Client(reconnect_on_failure=True)
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect("127.0.0.1", 1883, 60)
mqtt_client.loop_forever()  # start the MQTT client loop in a separate thread
