"""This file contains the TelemetryPubSub class which is a child class of BaseMQTTPubSub.
The TelemetryPubSub reads a telemetry file aggregated by a cron job running on the
PinePhone and publishes that data to the MQTT broker.
"""
import os
from time import sleep
from typing import Any
import schedule

from base_mqtt_pub_sub import BaseMQTTPubSub


class TelemetryPubSub(BaseMQTTPubSub):
    """This class reads a JSON file aggregated by the telemetry.py cron job running on
    the device and publishes that data to MQTT.

    Args:
        BaseMQTTPubSub (BaseMQTTPubSub): parent class written in the EdgeTech Core module
    """

    def __init__(
        self: Any,
        telemetry_pub_topic: str,
        telemetry_file_path: str,
        debug: bool = False,
        **kwargs: Any,
    ):
        """The TelemetryPubSub constructor takes a topic to publish data to and a file path to
        read telemetry data from and sends that data to the MQTT client.

        Args:
            telemetry_pub_topic (str): MQTT topic to publish the telemetry data to.
            telemetry_file_path (str): Path to the telemtry JSON saved by the cron job.
            debug (bool, optional): If the debug mode is turned on, log statements print to stdout.
        """
        # Pass enviornment variables as parameters (include **kwargs) in super().__init__()
        super().__init__(**kwargs)
        self.telemetry_pub_topic = telemetry_pub_topic
        self.telemetry_file_path = telemetry_file_path
        # include debug version
        self.debug = debug

        # Connect client in constructor
        self.connect_client()
        sleep(1)
        self.publish_registration("Telemetry Module Registration")

    def _publish_telemetry(self: Any) -> None:
        """Leverages edgetech-core functionality to publish a JSON payload to the MQTT
        broker on the topic specified in the class constructor after opening and reading
        the telemetry file.
        """
        with open(self.telemetry_file_path, "r", encoding="utf-8") as f_pointer:
            data = f_pointer.read()
            self.publish_to_topic(self.telemetry_pub_topic, data)

    def main(self: Any) -> None:
        """Main loop and function that setup the heartbeat to keep the TCP/IP
        connection alive and publishes the data to the MQTT broker and keeps the
        main thread alive."""
        # include schedule heartbeat in every main()
        schedule.every(10).seconds.do(
            self.publish_heartbeat, payload="Telemetry Module Heartbeat"
        )

        # send the payload to MQTT
        schedule.every(1).minutes.do(self._publish_telemetry)

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
        telemetry_file_path=str(os.environ.get("TELEMETRY_FILE_PATH")),
        mqtt_ip=os.environ.get("MQTT_IP"),
    )
    telemetry.main()
