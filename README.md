# edgetech-telemetry-pinephone
EdgeTech Telemetry module for the PinePhone

Telemetry data is read from sensor files that are mapped to the Docker container in `docker-compose.yml` and published to on the telemetry MQTT topic.

Current telemetry data being utilized:
```
battery capacity    :   /sys/class/power_supply/rk818-battery/capacity
uptime              :   /proc/uptime
```

## Run
```
git clone git@github.com:IQTLabs/edgetech-telemetry-pinephone.git
cd edgetech-telemetry-pinepone
docker compose up --build
```