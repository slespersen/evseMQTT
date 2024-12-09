FROM python:3-alpine

RUN apk add bluez

ENV BLE_ADDRESS="" \
    BLE_PASSWORD="" \
    UNIT="" \
    MQTT_BROKER="" \
    MQTT_PORT="1883" \
    MQTT_USER="" \
    MQTT_PASSWORD="" \
    LOGGING_LEVEL="INFO"

ADD . /app

WORKDIR /app

RUN pip install -r requirements.txt

CMD ["sh", "-c", "python main.py --address ${BLE_ADDRESS} --password ${BLE_PASSWORD} --unit ${UNIT} --mqtt --mqtt_broker ${MQTT_BROKER} --mqtt_port ${MQTT_PORT} --mqtt_user ${MQTT_USER} --mqtt_password ${MQTT_PASSWORD} --logging_level ${LOGGING_LEVEL}"]
