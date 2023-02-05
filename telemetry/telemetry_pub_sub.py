"""This file contains the TelemetryPubSub class which is a child class of BaseMQTTPubSub.
The TelemetryPubSub reads a telemetry file aggregated by a cron job running on the
PinePhone and publishes that data to the MQTT broker.
"""
import os
from time import sleep
from datetime import datetime
from typing import Any
import json
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
        battery_capacity_file_path: str,
        uptime_file_path: str,
        debug: bool = False,
        **kwargs: Any,
    ):
        """The TelemetryPubSub constructor takes a topic to publish data to and files to read
        telemetry from.

        Args:
            telemetry_pub_topic (str): MQTT topic to publish the telemetry data to.
            battery_capacity_file_path (str): Path to the PinePhone battery capacity
            file (i.e. /sys/class/power_supply/rk818-battery/capacity)
            battery_capacity_file_path (str): Path to the PinePhone uptime file (i.e. /proc/uptime)
            debug (bool, optional): If the debug mode is turned on, log statements print to stdout.
        """
        # Pass enviornment variables as parameters (include **kwargs) in super().__init__()
        super().__init__(**kwargs)
        self.telemetry_pub_topic = telemetry_pub_topic
        self.battery_capacity_file_path = battery_capacity_file_path
        self.uptime_file_path = uptime_file_path
        # include debug version
        self.debug = debug

        # Connect client in constructor
        self.connect_client()
        sleep(1)
        self.publish_registration("Telemetry Module Registration")

    def _publish_telemetry(self: Any) -> None:
        """Leverages edgetech-core functionality to publish a JSON payload to the MQTT
        broker on the topic specified in the class constructor after opening and reading
        the telemetry file(s).
        """

        # instantiate output dictionary
        result = {}

        # add timestamp
        result["timestamp"] = str(int(datetime.utcnow().timestamp()))

        # add battery power
        with open(self.battery_capacity_file_path, "r", encoding="utf-8") as f_pointer:
            data = f_pointer.read()
            result["battery_percentage"] = data.strip()

        # add uptime
        with open(self.uptime_file_path, "r", encoding="utf-8") as f_pointer:
            data = f_pointer.read()
            result["uptime_total_seconds"] = data.split(" ")[0]

        if self.debug:
            print(result)

        # publish JSON 'result' to MQTT topic
        out_json = self.generate_payload_json(
            push_timestamp=str(int(datetime.utcnow().timestamp())),
            device_type="Collector",
            id_="TEST",
            deployment_id=f"AISonobuoy-Arlington-{'TEST'}",
            current_location="-90, -180",
            status="Debug",
            message_type="Event",
            model_version="null",
            firmware_version="v0.0.0",
            data_payload_type="Telemetry",
            data_payload=json.dumps(result),
        )
        self.publish_to_topic(self.telemetry_pub_topic, out_json)

    def main(self: Any) -> None:
        """Main loop and function that setup the heartbeat to keep the TCP/IP
        connection alive and publishes the data to the MQTT broker and keeps the
        main thread alive."""
        # include schedule heartbeat in every main()
        schedule.every(10).seconds.do(
            self.publish_heartbeat, payload="Telemetry Module Heartbeat"
        )

        # send the payload to MQTT
        schedule.every(1).minute.do(self._publish_telemetry)

        while True:
            try:
                schedule.run_pending()
                # include a sleep so loop does not run at CPU time
                sleep(0.001)

            except KeyboardInterrupt as exception:
                if self.debug:
                    print(exception)


if __name__ == "__main__":
    telemetry = TelemetryPubSub(
        telemetry_pub_topic=str(os.environ.get("TELEMETRY_TOPIC")),
        battery_capacity_file_path=str(os.environ.get("BATTERY_CAPACITY_FILE_PATH")),
        uptime_file_path=str(os.environ.get("UPTIME_FILE_PATH")),
        mqtt_ip=os.environ.get("MQTT_IP"),
    )
    telemetry.main()
