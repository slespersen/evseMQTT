# evseMQTT

`evseMQTT` is a Python library designed for communicating with EVSE-based Electric Vehicle Charging Wallboxes using Bluetooth Low Energy (BLE), and exposing its data and controls to Home Assistant using MQTT Discovery.
Due to potential security concerns of WiFi connectivity, this library facilitates a local, no cloud connection to your EVSE device. It has been tested on the Besen BS20 model using a Raspberry Pi Zero 2 W.

The code base is by no means perfect or especially beautiful -- pragmatic hacks are applied where needed.
![Home Assistant Device view](https://raw.githubusercontent.com/slespersen/evseMQTT/refs/heads/main/evseMQTT_home_assistant.png)

## Features

`evseMQTT` provides the following functionalities:

- **Start/Stop Charging:** Control the charging process.
- **Set Maximum Amps:** Define the maximum amperage for a charging session.
- **Change Language:** Modify the language setting (note: this affects the smartphone app rather than the wallbox itself).
- **Device Name:** Set or change the name of the device.
- **Temperature Unit:** Set the preferred unit of temperature.
- **Phase detection**: Available phases are automatically identified.
- **Max amp detection**: Maximum amperage output is automatically detected.
- **Automatic Reconnect**: In case the Bluetooth connection is stale, and no message has been received for more than 35 seconds, the script will automatically reinitialize.

Additionally, `evseMQTT` allows you to read:

- **Current Consumption of Energy:** Monitor the energy consumption in kilowatt-hours (kWh).
- **Errors**: Monitor potential errors.
- **Phase characteristics**: Monitor voltage and amperage across the phases present on the charger.
- **Messages**: Monitor messages defined by the state of both the plug, the output and the status.
- **Total Consumption**: Monitor the total energy consumption (since last reset) in kilowatt-hours (kWh).
- **Temperature**: Monitor the current temperature.
- **Date & Time**: Get the devices current date and time.

## Home Assistant Integration

`evseMQTT` exposes basic control functionalities to Home Assistant via MQTT Discovery, enabling seamless integration and control within your home automation setup.

## Upcoming features

The following functions are in the making:

- **Automatic Temperature Unit Update**: Automatically updating of the enabled and disabled temperature unit sensor in Home Assistant to not pollute the different statistics.
- **Additional Status Messages**: Additional messages for both charge_start and charge_stop.

## Installation with pipx

install [pipx](https://pipx.pypa.io/latest/installation/)

```bash
sudo pipx install git+https://github.com/slespersen/evseMQTT
sudo ln -s ~/.local/bin/evseMQTT /usr/local/bin/evseMQTT
/usr/local/bin/evseMQTT --help
```

## Usage

`evseMQTT` is provided for running the library. Below are the arguments it accepts:

### Arguments

- `--address`: (Required) The BLE device address.
- `--password`: (Required) The BLE device password. Default is "123456".
- `--unit`: (Optional) The unit of measurement, for consumed power - kW or W. Default is "W".
- `--mqtt`: (Optional) Enable MQTT.
- `--mqtt_broker`: (Optional) The MQTT broker address.
- `--mqtt_port`: (Optional) The MQTT broker port.
- `--mqtt_user`: (Optional) The MQTT username.
- `--mqtt_password`: (Optional) The MQTT password.
- `--logging_level`: (Optional) The logging level. Default is "INFO".

### Example Command

Here's an example of how to run `main.py` with the necessary arguments:

```bash
evseMQTT --address "your_device_mac_address" \
               --password "your_6_digit_pin" \
               --unit "W" \
               --mqtt \
               --mqtt_broker "your_mqtt_broker_address" \
               --mqtt_port 1883 \
               --mqtt_user "your_mqtt_username" \
               --mqtt_password "your_mqtt_password" \
               --logging_level "DEBUG"
```

### Run as container

```bash

docker run -d --name evseMQTT \
      --restart always \
      -v /var/run/dbus:/run/dbus \
      -e BLE_ADDRESS="your_device_mac_address" \
      -e BLE_PASSWORD="your_6_digit_pin" \
      -e UNIT="W" \
      -e MQTT_ENABLED="true" \
      -e MQTT_BROKER="your_mqtt_broker_address" \
      -e MQTT_PORT=1883 \
      -e MQTT_USER="your_mqtt_username" \
      -e MQTT_PASSWORD="your_mqtt_password" \
      -e LOGGING_LEVEL="INFO" \
      ghcr.io/slespersen/evsemqtt:latest
```

### Run as systemd service

A systemd service file has been provided.

you need to create the environment file `/etc/default/evseMQTT` with the following content:

```bash
BLE_ADDRESS=AA:BB:CC:DD:EE:FF
BLE_PASSWORD=123456
UNIT="W"
MQTT_BROKER=_broker_
MQTT_PORT=1883
MQTT_USER=_user_
MQTT_PASSWORD=_password_
LOGGING_LEVEL=INFO
```

```bash
sudo curl https://raw.githubusercontent.com/slespersen/evseMQTT/refs/heads/main/evseMQTT.service -o /etc/systemd/system/evseMQTT.service

# create the config file and edit it
sudo nano /etc/default/evseMQTT

sudo systemctl daemon-reload

sudo systemctl enable evseMQTT.service

sudo systemctl start evseMQTT.service

sudo journalctl -f -u evseMQTT
```

### Handle bluetooth module crashes in container

In some cases the bluetooth module crashes and needs to be restarted.
This can be handled by adding the following arguments to the docker run command:

- `-cap-add=SYS_MODULE`
- `-v /lib/modules:/lib/modules:ro`
- `-e SYS_MODULE_TO_RELOAD="btusb"`

For usb bluetooth dongles use `btusb`, on a Raspberry Pi use `hci_uart`

### Determine BLE address for your EVSE

look for a mac address started with `ACP#` like this:

```bash
bluetoothctl scan le
```

results in something like this:

```plain
Discovery started
[CHG] Controller B8:27:EB:B4:51:EB Discovering: yes
[NEW] Device 12:34:56:78:99:00 ACP#NamedEVSE
```

## Caveats

This library is in no means complete, when compared to the original app - some features missing:

- Charging History
- LCD Brightness
- Password Reset
- Device Reset
- WiFi setup

Seemingly unexpected behavior, but working as intended:

- When changing the device name, the device will disconnect and the script will wait for 35 seconds, since the last received message, before reconnecting.

## Acknowledgements

A big thank you to the following contributors:

- [bakkers](https://github.com/bakkers) for documenting findings: https://gist.github.com/bakkerrs/cb75e3c3a337f8f38a3f84f4b49beaa5

- [johnwoo-nl](https://github.com/johnwoo-nl) for building emproto: https://github.com/johnwoo-nl/emproto/tree/main?tab=readme-ov-file

- [Phil242](https://github.com/Phil242), [FlorentVTT](https://github.com/FlorentVTT), and [DutchDevelop](https://github.com/DutchDevelop) for their original efforts in decoding the EVSE protocol

## Tested Devices

- **Besen BS20:** This library has been tested and verified to work with the Besen BS20 Electric Vehicle Charging Wallbox.

## License

This project is licensed under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue.

## Support

For any questions or issues, please open an issue.