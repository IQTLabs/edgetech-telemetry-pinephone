import subprocess
import json
import jc

cmd_output = ""
result = {}

# parse battery percentage
try:
    cmd_output = subprocess.check_output(["upower", "-d"], stderr=subprocess.STDOUT).decode('utf-8')
except Exception as e:
    print(e)

if cmd_output!="":
    jc_output = jc.parse('upower', cmd_output)
    json_str = json.dumps(jc_output,indent=1)
    json_obj = json.loads(json_str)
    
    for item in json_obj:
        if "device_name" in item and item['device_name'] == "/org/freedesktop/UPower/devices/battery_rk818_battery":
            if "percentage" in item['detail']:
                result["battery_percentage"] = item['detail']["percentage"]

# parse uptime
try:
    cmd_output = subprocess.check_output(["uptime"], stderr=subprocess.STDOUT).decode('utf-8')
except Exception as e:
    print(e)

if cmd_output!="":
    jc_output = jc.parse('uptime', cmd_output)
    json_str = json.dumps(jc_output,indent=1)
    json_obj = json.loads(json_str)
    
    if "uptime_total_seconds" in json_obj:
        result["uptime_total_seconds"] = json_obj["uptime_total_seconds"]

# save result json to file
print(result)

with open('sensor-data/telemetry_data.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=4)
