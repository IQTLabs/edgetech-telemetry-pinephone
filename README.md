# edgetech-telemetry-pinephone
EdgeTech Telemetry module for the PinePhone

Read telemetry JSON string from Docker bind mount and publish on the telemetry topic.

## Prerequisits
- Cron job to aggregate PinePhone telemetry in a file on the host OS. Cron job can be created with the following command:
```
cat <(sudo crontab -l) <(echo "* * * * * /usr/bin/python3 /home/mobian/edgetech-telemetry-pinephone/utils/telemetry.py") | sudo crontab -
```

## Run
```
git clone git@github.com:IQTLabs/edgetech-telemetry-pinephone.git
cd edgetech-telemetry-pinepone
docker compose up --build
```