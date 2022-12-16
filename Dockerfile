FROM python:3.11-slim

RUN pip install paho-mqtt==1.6.1
RUN apt update
#RUN apt install screen -y

WORKDIR /root
ADD BaseMQTTPubSub.py .
ADD TelemetryPinephone.py .

# variable passed via compose 
ARG BASE_MQTT_PUBLISH_TOPIC
ENV BASE_MQTT_PUBLISH_TOPIC=$BASE_MQTT_PUBLISH_TOPIC

ARG BASE_MQTT_SUBSCRIBE_TOPIC
ENV BASE_MQTT_SUBSCRIBE_TOPIC=$BASE_MQTT_SUBSCRIBE_TOPIC

CMD python -u TelemetryPinephone.py --mqtt-publish-topic $BASE_MQTT_PUBLISH_TOPIC --mqtt-subscribe-topic $BASE_MQTT_PUBLISH_TOPIC