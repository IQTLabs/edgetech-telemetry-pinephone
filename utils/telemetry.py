"""
This file collect relevant telemetry on the pinephone and writes them to a summary JSON file that
can then be accessed my an MQTT PubSub running in a docker container as OS commands cannot be
executed from a container.

Run this file, use the following cron job (you may have to change the path to the telemetry file):
pip3 install jc==1.22.4
crontab -e
* * * * * /usr/bin/python3 /home/mobian/ari_dev/edgetech-telemetry-pinephone/utils/telemetry.py

This cron job runs every minute, which is the minimum cadence at which a cron job can run.
"""
import subprocess
import json
import os
from datetime import datetime
import jc

# instantiate output dictionary
result = {}

# add timestamp
result["timestamp"] = str(int(datetime.utcnow().timestamp()))

# add battery power
result["battery_percentage"] = {
    key: val
    for dict_ in jc.parse(
        "upower",
        subprocess.check_output(["upower", "-d"], stderr=subprocess.STDOUT).decode(
            "utf-8"
        ),
    )
    for key, val in dict_.items()
}["detail"]["percentage"]

# add uptime
result["uptime_total_seconds"] = jc.parse(
    "uptime",
    subprocess.check_output(["uptime"], stderr=subprocess.STDOUT).decode("utf-8"),
)["uptime_total_seconds"]

# save
os.makedirs("/home/mobian/telemetry_data", exist_ok=True)
with open(
    "/home/mobian/telemetry_data/telemetry_data.json", "w+", encoding="utf-8"
) as f_pointer:
    json.dump(result, f_pointer, ensure_ascii=False, indent=4)
