import json
from .utils import Utils

class Commands:
    def __init__(self, ble_manager, device, logger):
        self.ble_manager = ble_manager
        self.device = device
        self.logger = logger  # Use the centralized logger

    async def login_request(self):
        command = Utils.build_command(self.device.info['serial'], self.device.ble_password, 32770)
        self.logger.debug(f"Generated command for: 32770 - login_request\n{command}")
        await self.ble_manager.message_producer(command)
        return command.hex()

    async def login_confirm(self):
        command = Utils.build_command(self.device.info['serial'], self.device.ble_password, 32769, [1])
        self.logger.debug(f"Generated command for: 32769 - login_confirm\n{command}")
        await self.ble_manager.message_producer(command)
        return command.hex()
        
    async def heartbeat(self):
        command = Utils.build_command(self.device.info['serial'], self.device.ble_password, 32771, [1])
        self.logger.debug(f"Generated command for: 32771 - heartbeat\n{command}")
        await self.ble_manager.message_producer(command)
        return command.hex()

    async def set_charge_fee(self):
        command = Utils.build_command(self.device.info['serial'], self.device.ble_password, 33028, [1, 1, 0, 0])
        self.logger.debug(f"Generated command for: 33028 - set_charge_fee\n{command}")
        await self.ble_manager.message_producer(command)
        return command.hex()

    async def get_charge_fee(self):
        command = Utils.build_command(self.device.info['serial'], self.device.ble_password, 33028, [2, 0])
        self.logger.debug(f"Generated command for: 33028 - get_charge_fee\n{command}")
        await self.ble_manager.message_producer(command)
        return command.hex()
        
    async def set_charge_service_fee(self):
        command = Utils.build_command(self.device.info['serial'], self.device.ble_password, 33029, [1, 1, 0, 0])
        self.logger.debug(f"Generated command for: 33029 - set_charge_service_fee\n{command}")
        await self.ble_manager.message_producer(command)
        return command.hex()
        
    async def get_charge_service_fee(self):
        command = Utils.build_command(self.device.info['serial'], self.device.ble_password, 33029, [2, 0])
        self.logger.debug(f"Generated command for: 33029 - get_charge_service_fee\n{command}")
        await self.ble_manager.message_producer(command)
        return command.hex()
        
    async def get_charge_status_record(self):
        command = Utils.build_command(self.device.info['serial'], self.device.ble_password, 32781)
        self.logger.debug(f"Generated command for: 32781 - get_charge_status_record\n{command}")
        await self.ble_manager.message_producer(command)
        return command.hex()
        
    async def set_charge_start(self, max_amps = 6):
        # if there's multiple phases, the line_id is 2 - otherwise 1
        line_id = 2 if self.device.info['phases'] == 3 else 1
        user_id = self.device.ble_user_id
        charge_id = Utils.generate_charge_id()
        is_reservation = 0
        start_date = Utils.timestamp_bytes()
        start_type = 1
        charge_type = 1
        param1 = [255, 255]
        param2 = [255, 255]
        param3 = [255, 255]
        command = Utils.build_command(self.device.info['serial'], self.device.ble_password, 32775, [line_id, user_id, charge_id, is_reservation, start_date, start_type, charge_type, param1, param2, param3, max_amps])
        self.logger.debug(f"Generated command for: 32775 - set_charge_start\n{command}")
        await self.ble_manager.message_producer(command)
        return command.hex()
    
    async def set_charge_stop(self):
        command = Utils.build_command(self.device.info['serial'], self.device.ble_password, 32776, [1, self.device.ble_user_id, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        self.logger.debug(f"Generated command for: 32776 - set_charge_stop\n{command}")
        await self.ble_manager.message_producer(command)
        return command.hex()
        
    async def get_config_version(self):
        command = Utils.build_command(self.device.info['serial'], self.device.ble_password, 33030)
        self.logger.debug(f"Generated command for: 33030 - get_config_version\n{command}")
        await self.ble_manager.message_producer(command)
        return command.hex()
        
    async def set_config_temperature_unit(self, unit):
        command = Utils.build_command(self.device.info['serial'], self.device.ble_password, 33042, [1, unit])
        self.logger.debug(f"Generated command for: 33042 - set_config_temperature_unit\n{command}")
        await self.ble_manager.message_producer(command)
        return command.hex()
        
    async def get_config_temperature_unit(self):
        command = Utils.build_command(self.device.info['serial'], self.device.ble_password, 33042, [2, 0])
        self.logger.debug(f"Generated command for: 33042 - get_config_temperature_unit\n{command}")
        await self.ble_manager.message_producer(command)
        return command.hex()
        
    async def set_config_language(self, language):
        command = Utils.build_command(self.device.info['serial'], self.device.ble_password, 33039, [1, language])
        self.logger.debug(f"Generated command for: 33039 - set_config_language\n{command}")
        await self.ble_manager.message_producer(command)
        return command.hex()
        
    async def get_config_language(self):
        command = Utils.build_command(self.device.info['serial'], self.device.ble_password, 33039, [2, 0])
        self.logger.debug(f"Generated command for: 33039 - get_config_language\n{command}")
        await self.ble_manager.message_producer(command)
        return command.hex()
        
    async def set_config_name(self, name):
        bytes = Utils.device_name(name)
        command = Utils.build_command(self.device.info['serial'], self.device.ble_password, 33032, [1, bytes])
        self.logger.debug(f"Generated command for: 33032 - set_config_name\n{command}")
        await self.ble_manager.message_producer(command)
        return command.hex()
        
    async def get_config_name(self):
        command = Utils.build_command(self.device.info['serial'], self.device.ble_password, 33032, [2, 0])
        self.logger.debug(f"Generated command for: 33032 - get_config_name\n{command}")
        await self.ble_manager.message_producer(command)
        return command.hex()
        
    async def set_config_time(self):
        timestamp = Utils.timestamp_bytes()
        command = Utils.build_command(self.device.info['serial'], self.device.ble_password, 33025, [1, timestamp])
        self.logger.debug(f"Generated command for: 33025 - set_config_time\n{command}")
        await self.ble_manager.message_producer(command)
        return command.hex()
        
    async def get_config_time(self):
        command = Utils.build_command(self.device.info['serial'], self.device.ble_password, 33025, [2, 0])
        self.logger.debug(f"Generated command for: 33025 - get_config_time\n{command}")
        await self.ble_manager.message_producer(command)
        return command.hex()
    
    async def set_config_output_amps(self, max_amps = 6):
        command = Utils.build_command(self.device.info['serial'], self.device.ble_password, 33031, [1, max_amps])
        self.logger.debug(f"Generated command for: 33031 - set_config_output_amps\n{command}")
        await self.ble_manager.message_producer(command)
        return command.hex()
    
    async def get_config_output_amps(self):
        command = Utils.build_command(self.device.info['serial'], self.device.ble_password, 33031, [2, 0])
        self.logger.debug(f"Generated command for: 33031 - get_config_output_amps\n{command}")
        await self.ble_manager.message_producer(command)
        return command.hex()
    
    async def set_config_lcd_brightness(self, brightness = 100):
        command = Utils.build_command(self.device.info['serial'], self.device.ble_password, 33122, [0, 2, brightness, 0, 0, 0, 0, 0])
        self.logger.debug(f"Generated command for: 33122 - set_config_lcd_brightness\n{command}")
        await self.ble_manager.message_producer(command)
        return command.hex()
    
    async def get_config_lcd_brightness(self):
        command = Utils.build_command(self.device.info['serial'], self.device.ble_password, 33122, [0, 1, 0, 1, 0, 0, 0, 0])
        self.logger.debug(f"Generated command for: 33122 - get_config_lcd_brightness\n{command}")
        await self.ble_manager.message_producer(command)
        return command.hex()
    
    async def set_config_password(self, password):
        if len(password) != 6:
            self.logger.warning(f"Incorrect PIN length -- it should be exactly 6 digits. No more, no less.")
            return
        
        # Convert the integer to a string to process each digit 
        str_password = str(password)
        
        # Convert each digit to its ASCII integer representation 
        password_integers = [ord(char) for char in str_password]
        
        command = Utils.build_command(self.device.info['serial'], self.device.ble_password, 33026, password_integers)
        self.logger.debug(f"Generated command for: 33026 - set_config_password\n{command}")
        await self.ble_manager.message_producer(command)
        return command.hex()