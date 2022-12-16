import os
from BaseMQTTPubSub import BaseMQTTPubSub
import paho.mqtt.client as mqtt
from time import sleep

class TelemetryPinephone(BaseMQTTPubSub):
    def __init__(self):
        super().__init__()
        self.mqtt_publish_topic = os.environ['BASE_MQTT_PUBLISH_TOPIC']
        self.mqtt_subscribe_topic = os.environ['BASE_MQTT_SUBSCRIBE_TOPIC']
        
    def mqtt_callback(self, client: mqtt.Client, _userdata: dict, msg: str) -> str:
        print("Message Topic:", msg.topic)
        print("Message Payload:", str(msg.payload.decode("utf-8")))
        
    def publishPinePhoneTelemetry(self):
        # PinePhone example
        # with open("/sys/bus/iio/devices/iio\:device2/in_magn_z_raw", "r") as f:
        # val = f.readlines()
        telemetry.publish_to_topic(telemetry.mqtt_publish_topic, "1234")

if __name__ == "__main__":
    telemetry = TelemetryPinephone()
    telemetry.connect_client()
    telemetry.add_subscribe_topic("/telemetry/#", telemetry.mqtt_callback)

    while(True):
        telemetry.publishPinePhoneTelemetry()
        sleep(5)
