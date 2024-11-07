

import paho.mqtt.client as mqtt


# MQTT event handlers
def on_connect(client, userdata, flags, rc):
    print(f"MQTT connected with result code " + str(rc))
    client.subscribe("test")


# MQTT Client Setup
mqtt_client = mqtt.Client(reconnect_on_failure=True)
mqtt_client.on_connect = on_connect
mqtt_client.connect("127.0.0.1", 1883, 60)
mqtt_client.loop_start()
