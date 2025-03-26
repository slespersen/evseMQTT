import asyncio
import logging
from bleak import BleakScanner, BleakClient, BleakError
from .constants import Constants

class BLEManager:
    def __init__(self, event_handler, logger, callback=None):
        self.connected_devices = {}
        self.available_devices = {}
        self.connectiondata = {}
        self.logger = logger  # Use the centralized logger
        self.queue = asyncio.Queue(5)
        self.callback = callback
        self.event_handler = event_handler  # Use the EventHandlers instance passed from MainManager
        self.last_message_time = asyncio.get_event_loop().time()
        self.message_timeout = 35  # 35 seconds timeout for message reception
        self.max_retries = 5  # Maximum number of retries for connection
        
        self.write_uuid = ""
        self.read_uuid = ""

        # Ensure bleak does not go bananas, if we set logging to DEBUG
        self.logger_bleak = logging.getLogger("bleak")
        self.logger_bleak.setLevel(logging.INFO)

    async def scan(self, device_addr = False):
        self.logger.info("Scanning for evse BLE devices...")
        try:
            devices = await BleakScanner.discover(return_adv=True)

            # Filter devices with "ACP#" in their name
            self.available_devices = {dev.address: (dev, adv_data) for dev, adv_data in devices.values() if "ACP#" in dev.name}
            
            if device_addr:
                return self.available_devices[device_addr][1].rssi

            for address, (device, adv_data) in self.available_devices.items():
                self.logger.info(f"Found device: {device.name} ({address})")
                self.connectiondata[address] = device

            return self.available_devices

        except BleakError as e:
            await self.manager.exit_with_error(f"BleakError during scanning: {e}")
            
    async def connect_device(self, address):
        if address in self.available_devices:
            for attempt in range(self.max_retries):
                self.logger.info(f"Connecting to {address}, attempt {attempt + 1}")
                try:
                    client = BleakClient(address, timeout=65.0)
                    await client.connect()

                    services = client.services
                    service_uuids = [service.uuid for service in services]

                    # Check service UUIDs to determine board type
                    if any(uuid.startswith("0000ffe5-") or uuid.startswith("0000ffe0-") for uuid in service_uuids):
                        self.logger.debug(f"Device ({address}) identified as new revision")
                        self.write_uuid = Constants.NEW_BOARD_WRITE_UUID
                        self.read_uuid = Constants.NEW_BOARD_READ_UUID
                    elif any(uuid.startswith("0003cdd0-") for uuid in service_uuids):
                        self.logger.debug(f"Device ({address}) identified as other revision")
                        self.write_uuid = Constants.REV_WRITE_UUID
                        self.read_uuid = Constants.REV_READ_UUID
                        self.event_handler.device.fallback = True
                    else:
                        self.logger.debug(f"Device ({address}) identified as old revision")
                        self.write_uuid = Constants.WRITE_UUID
                        self.read_uuid = Constants.READ_UUID

                    self.connected_devices[address] = client
                    self.logger.info(f"Connected to {address}")
                    await self.start_notifications(address, self.read_uuid)
                                        
                    self.event_handler.device.config = {"rssi": self.available_devices[address][1].rssi}
                    self._schedule_reconnect_check()
                    return True
                except BleakError as e:
                    self.logger.error(f"Attempt {attempt + 1} failed with BleakError: {e}")
                except Exception as e:
                    self.logger.error(f"Attempt {attempt + 1} failed with error: {e}")
                await asyncio.sleep(2)  # Wait a bit before retrying
            await self.manager.exit_with_error(f"Failed to connect to {address} after {self.max_retries} attempts")
            return False
        else:
            await self.manager.exit_with_error(f"Device {address} not found")
            return False

    async def start_notifications(self, address, characteristic_uuid):
        if address in self.connected_devices:
            self.logger.debug(f"Starting notifications for {characteristic_uuid} on {address}")
            client = self.connected_devices[address]
            await client.start_notify(characteristic_uuid, self._handle_notification_wrapper)
            self.logger.debug(f"Notifications started for {characteristic_uuid} on {address}")
            return True
        else:
            self.logger.error(f"Device {address} not connected")
            await self.manager.exit_with_error(f"Device {address} not connected")
            return False

    async def _handle_notification_wrapper(self, sender, data):
        self.last_message_time = asyncio.get_event_loop().time()
        await self.event_handler.receive_notification(sender, data)

    async def disconnect_device(self, address):
        if address in self.connected_devices:
            self.logger.info(f"Disconnecting from {address}...")
            client = self.connected_devices[address]

            if client.is_connected:
                await client.stop_notify(self.read_uuid)

            await client.disconnect()
            del self.connected_devices[address]
            self.logger.info(f"Disconnected from {address}")
            return True
        else:
            self.logger.error(f"Device {address} not connected")
            return False

    async def read_characteristic(self, address, characteristic_uuid):
        if address in self.connected_devices:
            self.logger.debug(f"Reading characteristic {characteristic_uuid} from {address}")
            client = self.connected_devices[address]
            data = await client.read_gatt_char(characteristic_uuid)
            self.logger.debug(f"Read data: {data}")
            return data
        else:
            self.logger.error(f"Device {address} not connected")
            await self.manager.exit_with_error(f"Device {address} not connected")
            return None

    async def write_characteristic(self, address, characteristic_uuid, data):
        if address in self.connected_devices:
            self.logger.debug(f"Writing to characteristic {characteristic_uuid} on {address}")
            client = self.connected_devices[address]
            await client.write_gatt_char(characteristic_uuid, data)
            self.logger.debug(f"Write complete")
            return True
        else:
            await self.manager.exit_with_error(f"Device {address} not connected")
            return False

    async def heartbeat(self, interval, address):
        while True:
            self.logger.debug(f"Retrieving RSSI for device {address}")
            rssi = await self.scan(address)
            self.event_handler.device.config = {"rssi": rssi}
            await asyncio.sleep(interval)

    async def message_consumer(self, address, characteristic_uuid):
        while True:
            if not self.connected_devices.get(address):
                self.logger.warning(f"Device {address} not connected. Attempting to reconnect...")
                await self.connect_device(address)
                await asyncio.sleep(1)
                continue

            message = await self.queue.get()
            await self.write_characteristic(address, characteristic_uuid, message)
            self.queue.task_done()

    async def message_producer(self, message):
        await self.queue.put(message)

    def _schedule_reconnect_check(self):
        asyncio.get_event_loop().call_later(self.message_timeout, self._check_reconnect)

    def _check_reconnect(self):
        if asyncio.get_event_loop().time() - self.last_message_time > self.message_timeout:
            self.logger.warning(f"No message received in the last {self.message_timeout} seconds. Requesting manager to restart.")
            asyncio.create_task(self.manager.restart_run())
        else:
            self._schedule_reconnect_check()