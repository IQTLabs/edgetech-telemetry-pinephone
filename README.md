# edgetech-telemetry-pinephone
EdgeTech Telemetry module for the PinePhone

Read telemetry JSON string from Docker bind mount and publish on the telemetry topic.

## Prerequisits
- Requires system telemetry to be collected and saved as JSON string on host machine. Run `utils/telemetry.py` in a screen session or cron job on host machine.

## Run
```
git clone git@github.com:IQTLabs/edgetech-telemetry-pinephone.git
cd edgetech-telemetry-pinepone
docker compose up --build
```