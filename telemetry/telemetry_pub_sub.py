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
import logging

from base_mqtt_pub_sub import BaseMQTTPubSub


class TelemetryPubSub(BaseMQTTPubSub):
    """This class reads a JSON file aggregated by the telemetry.py cron job running on
    the device and publishes that data to MQTT.

    Args:
        BaseMQTTPubSub (BaseMQTTPubSub): parent class written in the EdgeTech Core module
    """

    def __init__(
        self: Any,
        telemetry_json_topic: str,
        # a comma-separated string of the names of variables to report
        telemetry_variables_to_report: str,
        # a comma-separated string of file locations containing the values of the above variables
        telemetry_variables_file_locations: str,
        hostname: str,
        log_file: str,
        debug: bool = True,
        **kwargs: Any,
    ):
        """The TelemetryPubSub constructor takes a topic to publish data to and files to read
        telemetry from.

        Args:
            telemetry_json_topic (str): MQTT topic to publish the telemetry data to.
            battery_capacity_file_path (str): Path to the PinePhone battery capacity
            file (i.e. /sys/class/power_supply/rk818-battery/capacity)
            battery_capacity_file_path (str): Path to the PinePhone uptime file (i.e. /proc/uptime)
            debug (bool, optional): If the debug mode is turned on, log statements print to stdout.
        """
        # Pass environment variables as parameters (include **kwargs) in super().__init__()
        super().__init__(**kwargs)
        self.telemetry_json_topic = telemetry_json_topic
        self.telemetry_variables_to_report = telemetry_variables_to_report.split(",")
        self.telemetry_file_locations = telemetry_variables_file_locations.split(",")
        self.hostname = hostname
        self.log_file = log_file

        if debug:
            logging.getLogger().setLevel(logging.DEBUG)

        # Connect client in constructor
        self.connect_client()
        sleep(1)
        self.publish_registration("Telemetry Module Registration")

    def _apply_transformation(
        self: Any, variable_name: str, variable_value: str
    ) -> str:
        """Apply transformations to clean variable values. All values will be stripped. Known
        raw values extracted from pinephones with associated known variable names will undergo
        transformations to make them human-readable.
        """

        return_value = variable_value.strip()

        if variable_name == "uptime_total_seconds":
            return_value = return_value.split(" ")[0]

        if variable_name == "cpu_temp" or variable_name == "battery_temp":
            return_value = return_value[0:2]

        if variable_name == "mem_free":
            return_value = str(return_value.split()[4]) + "kb"

        if variable_name == "power_draw":
            return_value = "{:.2f}".format((int(return_value) / 1000000))

        return return_value

    def _publish_telemetry(self: Any) -> None:
        """Leverages edgetech-core functionality to publish a JSON payload to the MQTT
        broker on the topic specified in the class constructor after opening and reading
        the telemetry file(s).
        """

        # instantiate output dictionary
        result = {}

        # add timestamp
        result["timestamp"] = str(int(datetime.utcnow().timestamp()))

        # add variables and values to output dictionary
        for ptr in range(0, len(self.telemetry_variables_to_report)):
            variable_name = self.telemetry_variables_to_report[ptr]
            with open(
                self.telemetry_file_locations[ptr], "r", encoding="utf-8"
            ) as file_handle:
                variable_value = file_handle.read()
                variable_value = self._apply_transformation(
                    variable_name, variable_value
                )
                result[variable_name] = variable_value

        write_timestamp = str(int(datetime.utcnow().timestamp()))
        write_data = json.dumps(result)
        if self.log_file is not None:
            with open(self.log_file, "w+") as fh:
                fh.write(str(write_timestamp) + ": " + str(write_data) + "\n")

        logging.debug(result)

        # publish JSON 'result' to MQTT topic
        out_json = self.generate_payload_json(
            push_timestamp=str(int(datetime.utcnow().timestamp())),
            device_type="Collector",
            id_=self.hostname,
            deployment_id=f"AISonobuoy-Arlington-{self.hostname}",
            current_location="-90, -180",
            status="Debug",
            message_type="Event",
            model_version="null",
            firmware_version="v0.0.0",
            data_payload_type="Telemetry",
            data_payload=json.dumps(result),
        )
        self.publish_to_topic(self.telemetry_json_topic, out_json)

    def main(self: Any) -> None:
        """Main loop and function that setup the heartbeat to keep the TCP/IP
        connection alive and publishes the data to the MQTT broker and keeps the
        main thread alive."""
        # include schedule heartbeat in every main()
        schedule.every(10).seconds.do(
            self.publish_heartbeat, payload="Telemetry Module Heartbeat"
        )

        # send the payload to MQTT
        schedule.every(20).seconds.do(self._publish_telemetry)

        while True:
            try:
                schedule.run_pending()
                # include a sleep so loop does not run at CPU time
                sleep(0.001)

            except KeyboardInterrupt as exception:
                logging.debug(exception)


if __name__ == "__main__":
    # providing for backwards compatability with earlier versions of edgetech-telemetry-pinephone
    telemetry_variables_to_report = os.environ.get("TELEMETRY_VARIABLES")
    if telemetry_variables_to_report is None:
        telemetry_variables_to_report = "battery_percentage,uptime_total_seconds"

    telemetry_variables_file_locations = os.environ.get("TELEMETRY_FILE_LOCATIONS")
    if telemetry_variables_file_locations is None:
        telemetry_variables_file_locations = (
            str(os.environ.get("BATTERY_CAPACITY_FILE_PATH"))
            + ","
            + str(os.environ.get("UPTIME_FILE_PATH"))
        )

    # creating the telemeter
    telemetry = TelemetryPubSub(
        telemetry_json_topic=str(os.environ.get("TELEMETRY_JSON_TOPIC")),
        telemetry_variables_to_report=telemetry_variables_to_report,
        telemetry_variables_file_locations=telemetry_variables_file_locations,
        hostname=str(os.environ.get("HOSTNAME")),
        mqtt_ip=str(os.environ.get("MQTT_IP")),
        log_file=str(os.environ.get("TELEMETRY_LOG_FILE")),
        debug=bool(True if os.environ.get("DEBUG") == "True" else False),
    )
    telemetry.main()
