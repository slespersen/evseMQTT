FROM python:3-alpine

ENV BLE_ADDRESS="" \
    BLE_PASSWORD="" \
    UNIT="W" \
    MQTT_ENABLED="true" \
    MQTT_BROKER="" \
    MQTT_PORT="1883" \
    MQTT_USER="" \
    MQTT_PASSWORD="" \
    LOGGING_LEVEL="INFO" \
    SYS_MODULE_TO_RELOAD=""

ADD . /app

WORKDIR /app

RUN apk add --no-cache bluez && pip install -r requirements.txt

ENTRYPOINT ["/app/entrypoint.sh"]
