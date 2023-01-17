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
        env_variable: Any,
        c2_sub_topic: str,
        telemetry_pub_topic: str,
        debug: bool = False,
        **kwargs: Any,
    ):
        # Pass enviornment variables as parameters (include **kwargs) in super().__init__()
        super().__init__(**kwargs)
        self.env_variable = env_variable
        self.c2_sub_topic = c2_sub_topic
        self.telemetry_pub_topic = telemetry_pub_topic
        # include debug version
        self.debug = debug

        # Connect client in constructor
        self.connect_client()
        sleep(1)
        self.publish_registration("Telemetry Module Registration")

    def c2_sub_topic_callback(
        self: Any, _client: mqtt.Client, _userdata: Dict[Any, Any], msg: Any
    ) -> None:
        # Decode message:
        # Always publishing a JSON string with {timestamp: ____, data: ____,}
        # TODO: more on this to come w/ a JSON header after talking to Rob
        payload = json.loads(str(msg.payload.decode("utf-8")))

        # TODO Add C2 functions
        pass

    def publish_telemetry(self: Any) -> None:
        data = ""
        
        try:
            f = open('/sensor-data/telemetry_data.json')
            data = json.load(f)
            f.close()
        except Exception as e:
            print(e)

        print(data)

        if data:
            # TODO format as JSON
            #example_data = {
            #    "timestamp": str(int(datetime.utcnow().timestamp())),
            #    "data": "Example data payload",
            #}
            self.publish_to_topic(self.telemetry_pub_topic, json.dumps(data))
        else:
            print("no data to publish")

    def main(self: Any) -> None:
        # main funciton wraps functionality and always includes a while True
        # (make sure to include a sleep)

        # include schedule heartbeat in every main()
        schedule.every(10).seconds.do(
            self.publish_heartbeat, payload="Telemetry Module Heartbeat"
        )

        # If subscribing to a topic:
        self.add_subscribe_topic(self.c2_sub_topic, self.c2_sub_topic_callback)

        # example publish data every 10 minutes
        schedule.every(1).minutes.do(
            self.publish_telemetry
        )

        while True:
            try:
                # run heartbeat and anything else scheduled if clock is up
                schedule.run_pending()
                # include a sleep so loop does not run at CPU time
                sleep(0.001)

            except Exception as e:
                if self.debug:
                    print(e)


if __name__ == "__main__":
    # instantiate an instance of the class
    # any variables in BaseMQTTPubSub can be overriden using **kwargs
    # and enviornment variables should be in the docker compose (in a .env file)
    telemetry = TelemetryPubSub(
        env_variable=os.environ.get("ENV_VARIABLE"),
        c2_sub_topic=str(os.environ.get("C2_TOPIC")),
        telemetry_pub_topic=str(os.environ.get("TELEMETRY_TOPIC")),
        mqtt_ip=os.environ.get("MQTT_IP"),
    )
    # call the main function
    telemetry.main()