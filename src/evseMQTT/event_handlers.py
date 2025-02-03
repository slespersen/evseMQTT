from .parsers import Parsers
from .utils import Utils
import asyncio

class EventHandlers:
    def __init__(self, device, commands, logger, callback=None):
        self.logger = logger  # Use the centralized logger
        self.device = device
        self.commands = commands
        self.callback = callback

        # Registry of command values to handler methods
        self.handlers = {
            1: Parsers.login_beacon,
            2: Parsers.login_response,
            4: Parsers.single_ac_status,
            5: Parsers.charge_status,
            6: Parsers.charge_status,
            7: Parsers.charge_start,
            8: Parsers.charge_stop,
            #9: Parsers.charge_record,
            #10: Parsers.charge_record,
            13: Parsers.single_ac_status,
            257: Parsers.system_time,
            262: Parsers.version,
            263: Parsers.output_amps,
            264: Parsers.name,
            271: Parsers.system_language,
            274: Parsers.system_temperature_unit,
        }
        
        # Messages including topics for the commands
        # we want to forward
        self.forward_messages = {
            4: "charge",
            13: "charge",
            257: "config",
            263: "config",
            264: "config",
            271: "config",        
            274: "config",        
        }

    async def handle_notification(self, sender, message):
        self.logger.debug(f"Notification from {sender}: {message}")

        # Split the byte array on \x06\x01 and validate following bytes (serial)
        segments = Utils.split_message(message)
        
        for segment in segments:
            if segment:
                parsed_data = Utils.parse_bytearray(segment)
                cmd = parsed_data['cmd']
                self.logger.info(f"Received command {cmd}")
                
                self.logger.debug(f"Parsed data:\n{parsed_data}")
                
                data = None
                
                if cmd in self.handlers:
                    handler = self.handlers[cmd]
                    data = handler(parsed_data['data'], parsed_data['identifier'])
                    self.logger.debug(f"Parsed data\n{data}")

                    # Update device info if command 1 is received
                    if cmd == 1:
                        self.device.info = data

                    # Log device accepted login request if command 2 is received
                    if cmd == 2:
                        self.logger.info(f"Device accepted login request")
                        
                    # Update device info if command 262 is received
                    if cmd in [4, 13]:
                        self.logger.info(f"Device sent a single charge ac status")
                        
                        # If the unit is kW we divide by 1000, to achieve it in kW
                        if self.device.unit == "kW":
                            data['current_energy'] = data['current_energy'] / 1000
                        
                        self.device.charge = data
                        
                    # Device charge status -- not sure what we need these for
                    if cmd in [5, 6]:
                        self.logger.info(f"Device sent a charge status")
                        
                    # Device responded to charge_start
                    if cmd == 7:
                        self.logger.info(f"Device responded to charge_start: {data}")
                        
                    # Device responded to charge_stop
                    if cmd == 8:
                        self.logger.info(f"Device responded to charge_stop: {data}")
                    
                    # Device sent a charge record -- not sure what we need these for
                    #if cmd in [9, 10]:
                    #    self.logger.info(f"Device sent a charge record")

                    # Update device info if command 262 is received
                    if cmd == 262:
                        self.logger.info(f"Device responded with {cmd}, containing {data}")
                        self.device.info = data

                    # Update device config if command is related
                    if cmd in [257, 263, 264, 271, 274]:
                        self.logger.info(f"Device responded with {cmd}, containing {data}")
                        self.device.config = data
                     
                    # Device did not accept the password -- log error
                    if cmd == 341:
                        self.logger.error(f"Password was not accepted by device!")
                
                if cmd == 1 and self.device.initialization_state:
                    self.logger.info(f"Device sent login banner - requesting login")
                    await self.commands.login_request()
                    await self.commands.set_charge_fee()
                    await self.commands.set_charge_service_fee()
                    
                if cmd == 2 and self.device.info['software_version'] is None:
                    self.logger.info(f"Device sent response to login request - confirming login")
                    await self.commands.login_confirm()
                    await self.commands.get_config_temperature_unit()
                    await self.commands.get_config_version()
                    await self.commands.get_config_name()
                    await self.commands.get_config_output_amps()
                    await self.commands.get_config_language()
                    await self.commands.get_config_lcd_brightness()
                    await self.commands.set_config_time()
                    await self.commands.get_charge_status_record()
                    await asyncio.sleep(2)  # Ugly hack - but hey ... it works
                
                if cmd == 3 and self.device.initialization_state:
                    self.logger.info(f"Device sent heartbeat - replying")
                    await self.commands.heartbeat()
                    await self.commands.set_config_time()

                # Before we forward the message, we check if:
                #   - the callback exists
                #   - the cmd is in forwarded messages
                #   - data is not None
                #   - device has been correctly initialized
                if self.callback and cmd in self.forward_messages and data is not None and self.device.initialization_state:
                    topic = self.forward_messages[cmd]
                    self.callback(self.device.info['serial'], topic, getattr(self.device, topic))
                    
        return cmd