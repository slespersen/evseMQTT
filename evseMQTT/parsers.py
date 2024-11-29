from .constants import Constants
from .utils import Utils
from .mqttpayloads import MQTTPayloads

class Parsers:  
    def login_beacon(data, identifier):
        return {
            "serial": identifier,
            "type": data[0],
            "phases": Utils.get_phases(data[0]),
            "manufacturer": data[1:16].strip(b'\x00').decode('utf-8'),
            "model": data[17:32].strip(b'\x00').decode('utf-8'),
            "hardware_version": data[33:49].decode('utf-8'),
            "output_power": Utils.bytes_to_int_little(data[49:53]),
            "output_max_amps": data[53],
            "support": data[54:69].strip(b'\x00').decode('utf-8')
        }
  
    def login_response(data, identifier):
        return {
            "serial": identifier,
            "type": data[0],
            "phases": Utils.get_phases(data[0]),
            "manufacturer": data[1:16].strip(b'\x00').decode('utf-8'),
            "model": data[17:32].strip(b'\x00').decode('utf-8'),
            "hardware_version": data[33:49].decode('utf-8'),
            "output_power": Utils.bytes_to_int_little(data[49:53]),
            "output_max_amps": data[53],
            "support": data[54:69].strip(b'\x00').decode('utf-8')
        }
        
    def version(data, identifier):
        return {
            "hardware_version": data[0:15].decode('utf-8').strip(),
            "software_version": data[16:31].decode('utf-8').strip("\u0000"),
            "feature": Utils.bytes_to_long_little(data[32:36]),
        }

    def charge_record(data, identifier):
        log_kw = []
        if len(data) >= 157:
            for i in range(30):
                start = 96 + i * 2
                end = start + 2
                log_kw.append(Utils.bytes_to_integer(data[start:end], byteorder='little'))

        log_charge_data = []
        if len(data) >= 253:
            for i in range(48):
                start = 156 + i * 2
                end = start + 2
                charge_data = {
                    "kwh": Utils.bytes_to_integer(data[start:end], byteorder='little'),
                    "charge_fee": Utils.bytes_to_integer(data[start + 96:end + 96], byteorder='little') if len(data) >= 349 else 0,
                    "service_fee": Utils.bytes_to_integer(data[start + 192:end + 192], byteorder='little') if len(data) >= 445 else 0
                }
                log_charge_data.append(charge_data)

        return {
            "line_id": Utils.byte_to_integer(data[0]),
            "start_user": data[1:17].strip(b'\x00').decode('utf-8').strip(),
            "end_user": data[17:33].strip(b'\x00').decode('utf-8').strip(),
            "charge_id": data[33:49].strip(b'\x00').decode('utf-8').strip(),
            "has_reservation": Utils.byte_to_integer(data[49]),
            "start_type": Utils.byte_to_integer(data[50]),
            "charge_type": Utils.byte_to_integer(data[51]),
            "charge_param1": Utils.bytes_to_integer(data[52:54]),
            "charge_param2": Utils.bytes_to_integer(data[54:56]) * 0.001 if Utils.bytes_to_integer(data[54:56]) != 255 else 255.0,
            "charge_param3": Utils.bytes_to_integer(data[56:58]) * 0.01 if Utils.bytes_to_integer(data[56:58]) != 255 else 255.0,
            "reason": Utils.byte_to_integer(data[58]),
            "has_stop_charge": Utils.byte_to_integer(data[59]),
            "reservationDate": Utils.bytes_to_integer(data[60:64]),
            "start_date": Utils.bytes_to_int_little(data[64:68]),
            "end_date": Utils.bytes_to_int_little(data[68:72]),
            "duration": Utils.bytes_to_integer(data[72:76]),
            "start_battery": round(Utils.bytes_to_int_little(data[76:80]) * 0.01, 2),
            "end_battery": round(Utils.bytes_to_int_little(data[80:84]) * 0.01, 2),
            "number": round(Utils.bytes_to_int_little(data[84:88]) * 0.01, 4),
            "charge_price": Utils.bytes_to_integer(data[88:92]) * 0.01,
            "fee_type": Utils.byte_to_integer(data[92]),
            "charge_fee": Utils.bytes_to_integer(data[93:95]) * 0.01,
            "log_kw_length": Utils.bytes_to_integer(data[95:97]),
            "log_kw": log_kw,
            "log_charge_data": log_charge_data
        }

    def charge_status(data, identifier):
        return {
            "port": Utils.byte_to_integer(data[0]),
            "current_state": Utils.byte_to_integer(data[1]) if len(data) <= 74 or not Utils.byte_to_integer(data[74]) in [18, 19] else Utils.byte_to_integer(data[74]),
            "charge_id": data[2:18].strip(b'\x00').decode('utf-8'),
            "start_type": Utils.byte_to_integer(data[18]),
            "charge_type": Utils.byte_to_integer(data[19]),
            "charge_param1": Utils.bytes_to_integer(data[20:22]),
            "charge_param2": 655.35 if Utils.bytes_to_integer(data[22:24]) == 65535 else Utils.bytes_to_integer(data[22:24]) * 0.01,
            "charge_param3": 65535.0 if Utils.bytes_to_integer(data[24:26]) == 65535 else Utils.bytes_to_integer(data[24:26]) * 0.01,
            "reservation_date": Utils.bytes_to_integer(data[26:30], byteorder='little'),
            "user_id": data[30:46].strip(b'\x00').decode('utf-8'),
            "max_electricity": Utils.byte_to_integer(data[46]),
            "start_date": Utils.bytes_to_integer(data[47:51], byteorder='little'),
            "duration": Utils.bytes_to_integer(data[51:55], byteorder='little'),
            "start_battery": Utils.bytes_to_integer(data[55:59]) * 0.01,
            "charge_current_power": Utils.bytes_to_integer(data[59:63]) * 0.01,
            "number": str(round(Utils.bytes_to_integer(data[63:67]) * 0.01, 2)),
            "charge_price": Utils.bytes_to_integer(data[67:71], byteorder='little') * 0.01,
            "fee_type": Utils.byte_to_integer(data[71]),
            "charge_fee": Utils.bytes_to_integer(data[72:74], byteorder='little') * 0.01
        }

    def single_ac_status(data, identifier):
        error_info = (
            f"{int(data[21]):08b}{int(data[22]):08b}" if len(data) < 25 else
            f"{int(data[21]):08b}{int(data[22]):08b}{int(data[23]):08b}{int(data[24]):08b}"
        ).replace(' ', '0')
        
        plug_state = Utils.byte_to_integer(data[18])
        current_state = Utils.byte_to_integer(data[20])
        
        failure_details = Utils.get_failure_details(error_info)
        charging_status_code = Utils.charging_status(plug_state, current_state)
        
        inner_temp = -1.0 if Utils.bytes_to_integer(data[13:15]) == 255 else round((Utils.bytes_to_integer(data[13:15]) - 20000) * 0.01, 1)
        
        object = {
            "line_id": Utils.bytes_to_integer(data[0:1]),
            "error_info": error_info,
            "error_details": failure_details,
            "l1_voltage": round(Utils.bytes_to_integer(data[1:3]) * 0.1, 1),
            "l1_amperage": round(Utils.bytes_to_integer(data[3:5]) * 0.01, 1),
            "total_energy": round(Utils.bytes_to_int_little(data[5:9]) / 1000, 2),
            "current_amount": round(Utils.bytes_to_integer(data[9:13]) * 0.01, 1),
            "inner_temp_c": inner_temp,
            "inner_temp_f": Utils.convert_temperature(inner_temp),
            "outer_temp": -1.0 if Utils.bytes_to_integer(data[15:17]) == 255 else round((Utils.bytes_to_integer(data[15:17]) - 20000) * 0.01, 1),
            "emergency_btn_state": Utils.byte_to_integer(data[17]),
            "plug_state": Constants.PLUG_STATE[plug_state],
            "output_state": Constants.OUTPUT_STATE[Utils.byte_to_integer(data[19])],
            "current_state": Constants.CURRENT_STATE[current_state],
            "new_protocol": 1 if len(data) > 33 else 0,
            "charging_status": Constants.CHARGING_STATUS[charging_status_code],
            "charging_status_description": Constants.CHARGING_STATUS_DESCRIPTIONS[charging_status_code],
            "charger_status": Constants.CHARGER_STATUS[charging_status_code]
        }
        
        # Check if either l1_voltage or l1_amperage is zero
        if object['l1_voltage'] == 0 or object['l1_amperage'] == 0:
            object['current_energy'] = 0
        else:
            # Calculating power for single phase in kW 
            object['current_energy'] = (object['l1_voltage'] * object['l1_amperage']) / 1000 # kW

        # Parsing additional fields if data length exceeds 25
        l2_voltage, l2_amperage, l3_voltage, l3_amperage = None, None, None, None
        if len(data) > 25:
            object['l2_voltage'] = round(Utils.bytes_to_integer(data[25:27]) * 0.1, 1)
            object['l2_amperage'] = round(Utils.bytes_to_integer(data[27:29]) * 0.01, 1)
            object['l3_voltage'] = round(Utils.bytes_to_integer(data[29:31]) * 0.1, 1)
            object['l3_amperage'] = round(Utils.bytes_to_integer(data[31:33]) * 0.01, 1)
            
            # Calculating additional phases in kW
            l2_power = (object['l2_voltage'] * object['l2_amperage']) / 1000 # kW 
            l3_power = (object['l3_voltage'] * object['l3_amperage']) / 1000 # kW 
        
            # Total power is the sum of power across all three phases 
            object['current_energy'] = round(object['current_energy'] + l2_power + l3_power, 1)

        # Parsing the main return dictionary
        return object
        
    def output_amps(data, identifier):
        return {
            "charge_amps": Utils.byte_to_integer(data[1])
        }
        
    def name(data, identifier):
        return {
            "device_name": data[1:32].replace(b'\x00', b'').decode('utf-8', errors='replace').strip()
        }
        
    #@staticmethod
    def system_time(data, identifier):
        epoch = Utils.bytes_to_int_little(data[1:5])
        local_time = Utils.bytes_to_timestamp(epoch)
    
        return {
            "system_time": local_time,
            "system_time_raw": epoch
        }
        
    def system_language(data, identifier):
        return {
            "language": Utils.get_key_by_value(Constants.LANGUAGES, Utils.byte_to_integer(data[1]))
        }
        
    def system_temperature_unit(data, identifier):
        return {
            "temperature_unit": Utils.get_key_by_value(Constants.TEMPERATURE_UNIT, Utils.byte_to_integer(data[1]))
        }
        
    def charge_start(data, identifier):
        return {
            "line_id": Utils.byte_to_integer(data[0]),
            "reservation_result": Constants.CHARGE_START_RESERVATION[Utils.byte_to_integer(data[1])],
            "start_result": Utils.byte_to_integer(data[2]),
            "error_reason": Constants.CHARGE_START_ERROR[Utils.byte_to_integer(data[3])],
            "output_amps": Utils.byte_to_integer(data[4]),
        }
        
    def charge_stop(data, identifier):
        return {
            "line_id": Utils.byte_to_integer(data[0]),
            "stop_result": Constants.STOP_REASON[Utils.byte_to_integer(data[1])],
            "error_reason": Utils.byte_to_integer(data[2]),
        }