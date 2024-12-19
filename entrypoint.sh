#!/usr/bin/env sh

# if configured as HA addon export options to env
if [ -f "/data/options.json" ]; then
   export $(jq -r 'to_entries | .[] | "\(.key)=\(.value)"' "/data/options.json")
fi

MQTT_ENABLED=${MQTT_ENABLED:-"true"}
MQTT_ARGS=""
SYS_MODULE_TO_RELOAD=${SYS_MODULE_TO_RELOAD:-""}

if [ "${MQTT_ENABLED}" = "true" ]; then
    MQTT_ARGS="--mqtt --mqtt_broker ${MQTT_BROKER} --mqtt_port ${MQTT_PORT} --mqtt_user ${MQTT_USER} --mqtt_password ${MQTT_PASSWORD}"
fi

if [ -n "${SYS_MODULE_TO_RELOAD}" ]; then
    echo "sys module reload enabled for: ${SYS_MODULE_TO_RELOAD}"
    if [ -d /lib/modules/ ]; then
      echo "reload module: ${SYS_MODULE_TO_RELOAD}"
      modprobe -r "${SYS_MODULE_TO_RELOAD}"
      sleep 2
      modprobe "${SYS_MODULE_TO_RELOAD}"
      sleep 2
      echo "sys module reload done"
    else
      echo "modules folder '/lib/modules/' not mounted. skip reload."
    fi
fi

echo "Starting evseMQTT ..."

/usr/local/bin/evseMQTT ${MQTT_ARGS} \
      --address "${BLE_ADDRESS}" \
      --password "${BLE_PASSWORD}" \
      --unit "${UNIT}" \
      --logging_level "${LOGGING_LEVEL}"
