import struct
from .constants import Constants
from datetime import datetime, timezone, timedelta

class Utils:
    @staticmethod
    def build_command(serial: int, password: str, cmd: int, data: list[int] = None) -> bytearray:
        # Flatten data if it contains nested lists
        if data is not None:
            flat_data = [] 
            for item in data: 
                if isinstance(item, list):
                    flat_data.extend(item) 
                else: 
                    flat_data.append(item)
            data = flat_data
        else:
            data = []

        # Calculate length correctly
        length = 25 + len(data)
        
        packet = bytearray()

        # Add header
        packet.extend([6, 1])

        # Add length
        packet.extend(struct.pack('>H', length))

        # Add reserved byte
        packet.append(0)

        # Add serial (little-endian)
        packet.extend(struct.pack('<Q', int(serial)))

        # Add password (ASCII bytes)
        packet.extend(password.encode('ascii'))

        # Add command (2-byte integer)
        packet.extend(struct.pack('>H', cmd))

        # Add data if it exists
        if data:
            packet.extend(data)

        # Calculate checksum (sum of all bytes % 0xFFFF)
        checksum = sum(packet) % 0xFFFF
        
        # Add the checksum (2-byte integer)
        packet.extend(struct.pack('>H', checksum))

        # Add end-byte
        packet.extend([15, 2])

        return packet
        
    @staticmethod    
    def parse_bytearray(byte_array: bytearray):
        # Extract segments based on positions and convert to appropriate formats
        parsed_data = {
            "header": byte_array[0:2],
            "data_length": byte_array[2:4],
            "reserved": byte_array[4:5],
            "identifier": Utils.byte_to_string(byte_array[5:13]),
            "password": byte_array[13:19],
            "cmd": int.from_bytes(byte_array[19:21], byteorder='big'),
            "data": byte_array[21:-4],
            "checksum": byte_array[-4:-2],
            "end_byte": byte_array[-2:]
        }

        return parsed_data
    
    @staticmethod
    def split_message(message):
        # Define the marker and capture the serial bytes
        marker = b'\x06\x01'
        original_serial_bytes = message[5:13]

        # Split the byte array on the marker
        segments = message.split(marker)
        
        valid_segments = []
        current_segment = marker + segments[0]  # Re-add the marker to the first segment

        for i in range(1, len(segments)):
            segment = segments[i]
            # Check if the segment starts with the original serial bytes after the marker
            if segment[:8] == original_serial_bytes:
                # If valid, finalize the current segment and start a new one
                valid_segments.append(current_segment)
                current_segment = marker + segment
            else:
                # Accumulate the invalid part to the current segment
                current_segment += segment  # Avoid re-adding the marker

        # Add the last accumulated segment
        valid_segments.append(current_segment)
        
        return valid_segments
   
    # Byte manipulation
    @staticmethod
    def byte_to_integer(byte):
        return byte & 0xFF

    @staticmethod
    def bytes_to_int_little(bytes): 
        """Combine bytes into an unsigned integer (little-endian).""" 
        return (bytes[3] & 0xFF) | ((bytes[0] & 0xFF) << 24) | ((bytes[1] & 0xFF) << 16) | ((bytes[2] & 0xFF) << 8)
        
    @staticmethod 
    def bytes_to_long_little(bytes): 
        """Convert bytes to long in little-endian format.""" 
        return Utils.bytes_to_int_little(bytes) & 0xFFFFFFFF

    @staticmethod
    def bytes_to_integer(bytes, byteorder='big'):
        return int.from_bytes(bytes, byteorder=byteorder)
        
    @staticmethod
    def byte_to_string(byte_array):
        return ''.join(f'{byte:02X}' for byte in byte_array)
        
    @staticmethod
    def timestamp_bytes():
        # Get current time
        current_time = datetime.now()
        
        # Cast to integers
        unix_timestamp = int(current_time.timestamp())
        
        # Convert to 4 bytes
        timestamp_bytes = unix_timestamp.to_bytes(4, byteorder='big')
        
        return list(timestamp_bytes)
        
    @staticmethod
    def bytes_to_timestamp(bytes):
        local_time = datetime.fromtimestamp(bytes)
        return local_time.isoformat()
            
    @staticmethod
    def device_name(name):
        # Convert string to bytes
        prefixed_name = f"ACP#{name}"
        bytes_arr = bytearray(prefixed_name.encode('ascii'))
    
        # Ensure the byte array is of length 15
        if len(bytes_arr) > 15:
            bytes_arr = bytes_arr[:15]
        else:
            bytes_arr.extend(bytearray([32] * (15 - len(bytes_arr))))
        
        # Pad to length 32 with zeros
        if len(bytes_arr) < 32:
            bytes_arr.extend(bytearray(32 - len(bytes_arr)))
        
        return list(bytes_arr)

    @staticmethod
    def get_failure_details(error_info):
        return Constants.ERRORS.get(error_info.find('1'), "No Error")

    @staticmethod 
    def get_phases(type): 
        types = {10, 11, 12, 13, 14, 15, 22, 23, 24, 25} 
        return 3 if type in types else 1

    @staticmethod
    def generate_charge_id():
        # Get the current time in the specified format
        current_time = datetime.now().strftime("%Y%m%d%H%M")
        id = current_time + "1337"

        # Convert the ID to a list of 16 bytes
        byte_list = id.encode('ascii')  # Encode the string to bytes

        # Ensure the byte_list is exactly 16 bytes long (fill with zeros if shorter)
        byte_list = byte_list.ljust(16, b'\x00')

        return list(byte_list)

    @staticmethod
    def charging_status(plug_state, current_state):
    
        charging_status = None
    
        if plug_state is None or current_state is None:
            return

        if current_state == 1:
            charging_status = 8
        elif current_state in [2, 3]:
            charging_status = 11
        elif current_state == 10:
            charging_status = 9
        elif current_state == 11:
            charging_status = 10
        elif current_state == 12:
            charging_status = 7
        elif current_state == 13:
            charging_status = 1
        elif current_state == 14:
            if plug_state == 4:
                charging_status = 2
            elif plug_state == 2:
                charging_status = 3
        elif current_state == 15:
            if plug_state in [4, 2]:
                charging_status = 4
        elif current_state == 17:
            charging_status = 5
        elif current_state == 20:
            charging_status = 6
            
        return charging_status
        
    @staticmethod    
    def get_key_by_value(dictionary, target_value): 
        for key, value in dictionary.items(): 
            if value == target_value: 
                return key 
        return None

    @staticmethod
    def convert_temperature(temp_str):
        temp = float(temp_str)
        
        # Convert from Celsius to Fahrenheit
        converted_temp = temp * 9 / 5 + 32

        # Round to 2 decimal places
        rounded_temp = round(converted_temp, 2)
        return str(rounded_temp)