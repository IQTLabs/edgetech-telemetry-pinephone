FROM iqtlabs/edgetech-core:latest

RUN pip install paho-mqtt==1.6.1
RUN apt update

WORKDIR /root
ADD TelemetryPinephone.py .

# variable passed via compose 
ARG BASE_MQTT_PUBLISH_TOPIC
ENV BASE_MQTT_PUBLISH_TOPIC=$BASE_MQTT_PUBLISH_TOPIC

ARG BASE_MQTT_SUBSCRIBE_TOPIC
ENV BASE_MQTT_SUBSCRIBE_TOPIC=$BASE_MQTT_SUBSCRIBE_TOPIC

CMD python -u TelemetryPinephone.py --mqtt-publish-topic $BASE_MQTT_PUBLISH_TOPIC --mqtt-subscribe-topic $BASE_MQTT_PUBLISH_TOPIC