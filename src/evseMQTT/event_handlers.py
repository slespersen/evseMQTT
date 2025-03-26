from .parsers import Parsers
from .utils import Utils
from .constants import Constants
import asyncio

class EventHandlers:
    def __init__(self, device, commands, logger, callback=None):
        self.logger = logger  # Use the centralized logger
        self.device = device
        self.commands = commands
        self.callback = callback
        self.cache_data = None
        self.message_length = 0

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
        
    async def receive_notification(self, sender, byte_array):
        self.logger.debug(f"Notification from {sender}: {byte_array}")

        packet_header = Constants.PACKET_HEADER
        if Utils.byte_to_string(byte_array[:2] if len(byte_array) >= 2 else byte_array[:1]) == packet_header:
            self.logger.debug(f"Packet Header OK")
            self.cache_data = byte_array
            if len(byte_array) >= 4:
                self.message_length = ((byte_array[2] << 8) + byte_array[3]) & 255
                if self.message_length > len(byte_array):
                    return
                await self.process_notification(sender, byte_array)
                return
            
            self.message_length = 0
            return

        if self.cache_data is None:
            self.logger.debug(f"No cache_data found")
            return

        if self.message_length == 0:
            self.message_length = len(self.cache_data) + len(byte_array)

        try:
            combined_data = self.cache_data + byte_array
            if self.message_length > len(combined_data):
                self.cache_data = combined_data
                return

            await self.process_notification(sender, combined_data)
            self.cache_data = None
            self.message_length = 0
        except Exception as e:
            self.logger.error(f"Exception occurred: {e}")

    async def process_notification(self, sender, byte_array):
        if len(byte_array) >= 25 and Utils.byte_to_string(byte_array[:2]) == Constants.PACKET_HEADER:
            length = ((byte_array[2] << 8) + byte_array[3]) & 255
            reserved_byte = byte_array[4]
            serial = Utils.byte_to_string(Utils.get_bytes(byte_array, 5, 12))

            self.logger.debug(f"Data length: {length}, Key type: {reserved_byte}, Serial number: {serial}")
            byte_array2 = bytearray(1)

            if reserved_byte == 0:
                cmd_byte = Utils.byte_to_string(Utils.get_bytes(byte_array, 19, 20))
                cmd = int(cmd_byte, 16)
                if cmd != 3:
                    byte_array2 = Utils.get_bytes(byte_array, 21, length - 5)
                    self.cache_data = None

            if byte_array2 is None:
                self.logger.debug(f"Data error: {Utils.byte_to_string(byte_array)}")
                return

            crc_length = length - 4
            bytes_val = Utils.get_bytes(byte_array, crc_length, length - 3)
            checksum = (bytes_val[0] << 8) + (bytes_val[1] & 0xFF)
            checksum_calc = sum(byte_array[i] & 0xFF for i in range(crc_length))

            if checksum_calc % 65536 != checksum:
                self.logger.debug("Checksum failed")
                return

            self.logger.debug("Checksum OK")

            self.logger.debug(f"Unencrypted data length: {len(byte_array2)}, CMD[0x{cmd_byte}]")
            await self.handle_notification(sender, byte_array)

            if len(byte_array) > length:
                await self.process_notification(sender, Utils.get_bytes(byte_array, length, len(byte_array) - 1))
                
    async def handle_notification(self, sender, message):
        # Split the byte array on \x06\x01 and validate following bytes (serial)
        #segments = Utils.split_message(message)
        #self.logger.debug(f"Segments: {segments}")
        
        #for segment in segments:
        #    if segment:
        #parsed_data = Utils.parse_bytearray(segment)
        parsed_data = Utils.parse_bytearray(message)
        cmd = parsed_data['cmd']
        self.logger.debug(f"Received command {cmd}")
        
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
                self.logger.debug(f"Device responded with {cmd}, containing {data}")
                self.device.info = data
            # Update device config if command is related
            if cmd in [257, 263, 264, 271, 274]:
                self.logger.debug(f"Device responded with {cmd}, containing {data}")
                self.device.config = data
             
            # Device did not accept the password -- log error
            if cmd == 341:
                self.logger.error(f"Password was not accepted by device!")
        
        if cmd == 1 and self.device.initialization_state and not self.device.logged_in:
            self.logger.info(f"Device sent login banner - requesting login")
            await self.commands.login_request()
            await self.commands.set_charge_fee()
            await self.commands.set_charge_service_fee()
            
        if cmd == 2 and self.device.info['software_version'] is None and not self.device.logged_in:
            self.logger.info(f"Device sent response to login request - confirming login")
            
            await self.commands.login_confirm()
            
            self.device.logged_in = True
            
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