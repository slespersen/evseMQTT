import argparse
import asyncio
import logging
import signal
import sys
from evseMQTT import BLEManager, Constants, Device, EventHandlers, Commands, Logger, MQTTClient, MQTTCallback, MQTTPayloads, Utils

class Manager:
    def __init__(self, address, ble_password, unit, mqtt_enabled=False, mqtt_settings=None, logging_level=logging.INFO, rssi=False):
        self.setup_logging(logging_level)
        self.logger = logging.getLogger("evseMQTT")
        debug = logging_level == logging.DEBUG  # Determine if debug logging is enabled
        
        self.device = Device(address)
        
        # Set the energy consumption unit
        self.device.unit = unit
        
        # Set the RSSI monitoring
        self.device.rssi = rssi
        
        # Set the BLE password
        self.device.ble_password = ble_password
        
        self.address = address

        # Correct order of instantiation
        self.commands = Commands(ble_manager=None, device=self.device, logger=self.logger)
        self.event_handlers = EventHandlers(device=self.device, commands=self.commands, logger=self.logger)
        self.ble_manager = BLEManager(event_handler=self.event_handlers, logger=self.logger)
        self.ble_manager.manager = self
        
        # Update ble_manager in commands now that it is created
        self.commands.ble_manager = self.ble_manager

        self.mqtt_client = None
        self.mqtt_callback = None
        self.mqtt_payloads = None
       # self.rssi = rssi

        if mqtt_enabled and mqtt_settings:
            self.mqtt_client = MQTTClient(logger=self.logger, **mqtt_settings)
            self.mqtt_client.connect()
            self.event_handlers.callback = self.mqtt_client.publish_state

    def setup_logging(self, logging_level):
        logging.basicConfig(level=logging_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    async def run(self, address):
        await self.ble_manager.scan()
        
        self.logger.info(f"Connecting...")
        
        if await self.ble_manager.connect_device(address):
            self.logger.info(f"Connected.")
            
            # Start the producer and consumer tasks
            consumer = asyncio.create_task(self.ble_manager.message_consumer(address, self.ble_manager.write_uuid))
            
            try:
                self.logger.info("Waiting for device initialization...")
                
                while not self.device.initialization_state:
                    self.logger.info(f"Device not initialized yet, waiting...")
                    await asyncio.sleep(1)

                self.logger.info(f"Device initialized with serial: {self.device.info['serial']}. Proceeding with login request.")
                
                while self.device.info['software_version'] is None:
                    self.logger.info(f"Waiting for software version...")
                    await asyncio.sleep(1)
                
                # Ensure that the following are true:
                #   - the MQTT client is required
                #   - the MQTT client is not already connected
                #   - the EVSE serial has been retrieved
                #   - the EVSE software_version has been retrieved
                if self.mqtt_client and not self.mqtt_client.connected and self.device.info['serial'] is not None and self.device.info['software_version'] is not None:
                    # Setup the MQTT payloads
                    self.mqtt_payloads = MQTTPayloads(device=self.device)
                    
                    # Setup the MQTT callback function
                    self.mqtt_callback = MQTTCallback(device=self.device, commands=self.commands)
                    
                    # Generate discovery payloads
                    discovery_payloads = self.mqtt_payloads.discovery()
                    
                    # Post discovery payloads
                    self.mqtt_client.publish_discovery(discovery_payloads)
                    
                    # Subscribe to the command topic
                    self.mqtt_client.subscribe(f"evseMQTT/{self.device.info['serial']}/command")
                    
                    # Setup the callback function for handling messages
                    self.mqtt_client.set_on_message(self.mqtt_callback.delegate)
                    
                    # Post online to availability topic
                    self.mqtt_client.publish_availability(self.device.info['serial'], "online")
                
                if self.device.rssi:
                    heartbeat = asyncio.create_task(self.ble_manager.heartbeat(60, address))
                
                while True:                
                    await asyncio.sleep(1)  # Example interval for ad-hoc message sending
                    self.logger.debug(f"Idling...")

            except (KeyboardInterrupt, SystemExit):
                # Handling cleanup on keyboard interrupt
                self.logger.info("Interrupted, cleaning up...")            
                
                # Wait for queue to be empty and disconnect the device
                await self.ble_manager.queue.join()
                await self.ble_manager.disconnect_device(address)
            finally:
                self.cleanup()

    def cleanup(self):
        if self.mqtt_client:
            self.mqtt_client.publish_availability(self.device.info['serial'], "offline")
            self.mqtt_client.disconnect()

    def handle_exit(self, signum, frame):
        self.logger.info(f"Signal {signal.Signals(signum).name} received, cleaning up...")
        self.cleanup()
        sys.exit(0)
        
    async def restart_run(self, address=None):
        if address is None:
            address = self.address
        
        self.logger.info("Restarting run function due to inactivity.")

        # Reset initialization_state and software_version
        self.device.initialization_state = False
        self.device.info = {'software_version': None}
        
        await self.run(address)

    async def exit_with_error(self, error):
        self.logger.error(f"Error encountered:\n{error}")
        # Perform necessary cleanup actions
        if self.mqtt_client:
            self.mqtt_client.publish_availability(self.device.info['serial'], "offline")
            self.mqtt_client.disconnect()
        
        tasks = [task for task in asyncio.all_tasks() if task is not asyncio.current_task()]
        
        for task in tasks:
            task.cancel()
        
        await asyncio.gather(*tasks, return_exceptions=True)
        
        self.logger.info("All tasks cancelled, exiting...")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="BLE Manager")
    parser.add_argument("--address", type=str, required=True, help="BLE device address")
    parser.add_argument("--password", type=str, required=True, help="BLE device password")
    parser.add_argument("--unit", type=str, default="W", help="Set the unit of measurement, for consumed power - kW or W")
    parser.add_argument("--mqtt", action='store_true', help="Enable MQTT")
    parser.add_argument("--mqtt_broker", type=str, help="MQTT broker address")
    parser.add_argument("--mqtt_port", type=int, help="MQTT broker port")
    parser.add_argument("--mqtt_user", type=str, help="MQTT username")
    parser.add_argument("--mqtt_password", type=str, help="MQTT password")
    parser.add_argument("--rssi", action='store_true', help="Monitor Received Signal Strength Indicator")
    parser.add_argument("--logging_level", type=str, default="INFO", help="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)")
    args = parser.parse_args()

    mqtt_settings = {
        "client_id": "evseMQTTClient",
        "broker": args.mqtt_broker,
        "port": args.mqtt_port,
        "username": args.mqtt_user,
        "password": args.mqtt_password
    } if args.mqtt else None
    
    logging_level = getattr(logging, args.logging_level.upper(), logging.INFO)
    manager = Manager(args.address, ble_password=args.password, unit=args.unit, mqtt_enabled=args.mqtt, mqtt_settings=mqtt_settings, rssi=args.rssi, logging_level=logging_level)
    
    # Register signal handlers for common termination signals
    signals = [signal.SIGINT, signal.SIGTERM, signal.SIGQUIT, signal.SIGABRT]
    for sig in signals:
        signal.signal(sig, manager.handle_exit)
    
    asyncio.run(manager.run(args.address))

if __name__ == "__main__":
    main()