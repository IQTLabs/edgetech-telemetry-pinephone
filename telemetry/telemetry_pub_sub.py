import os
from time import sleep
import json
from typing import Any, Dict
import schedule
from datetime import datetime
import paho.mqtt.client as mqtt

from base_mqtt_pub_sub import BaseMQTTPubSub

# inherit functionality from BaseMQTTPubSub parent this way
class TelemetryPubSub(BaseMQTTPubSub):
    def __init__(
        self: Any,
        telemetry_pub_topic: str,
        debug: bool = False,
        **kwargs: Any,
    ):
        # Pass enviornment variables as parameters (include **kwargs) in super().__init__()
        super().__init__(**kwargs)
        self.telemetry_pub_topic = telemetry_pub_topic
        # include debug version
        self.debug = debug

        # Connect client in constructor
        self.connect_client()
        sleep(1)
        self.publish_registration("Telemetry Module Registration")

    def publish_telemetry(self: Any) -> None:        
        with open('/sensor-data/telemetry_data.json', "r") as f:
            data = f.read()
            self.publish_to_topic(self.telemetry_pub_topic, data)

    def main(self: Any) -> None:
        # include schedule heartbeat in every main()
        schedule.every(10).seconds.do(
            self.publish_heartbeat, payload="Telemetry Module Heartbeat"
        )

        schedule.every(1).minutes.do(
            self.publish_telemetry
        )

        while True:
            try:
                schedule.run_pending()
                # include a sleep so loop does not run at CPU time
                sleep(0.001)

            except Exception as e:
                if self.debug:
                    print(e)


if __name__ == "__main__":
    telemetry = TelemetryPubSub(
        telemetry_pub_topic=str(os.environ.get("TELEMETRY_TOPIC")),
        mqtt_ip=os.environ.get("MQTT_IP"),
    )
    telemetry.main()