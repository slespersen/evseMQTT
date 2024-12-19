class Device:
    def __init__(self, mac):
        self.initialization_state = False
        self.ble_password = "123456"
        self.ble_user_id = [101, 118, 115, 101, 77, 81, 84, 84, 0, 0, 0, 0, 0, 0, 0, 0] # evseMQTT in ascii 16 bytes
        self.unit = "W"
        self._type = None
        self._phases = None
        self._manufacturer = None
        self._model = None
        self._hardware_version = None
        self._software_version = None
        self._output_power = None
        self._output_max_amps = None
        self._feature = None
        self._support = None
        self._mac = mac
        self._serial = None
        self._line_id = None
        self._start_user = None
        self._end_user = None
        self._charge_id = None
        self._has_reservation = None
        self._start_type = None
        self._charge_type = None
        self._charge_param1 = None
        self._charge_param2 = None
        self._charge_param3 = None
        self._reason = None
        self._has_stop_charge = None
        self._reservationDate = None
        self._start_date = None
        self._end_date = None
        self._duration = None
        self._start_battery = None
        self._end_battery = None
        self._number = None
        self._charge_price = None
        self._fee_type = None
        self._charge_fee = None
        self._log_kw_length = None
        self._log_kw = None
        self._log_charge_data = None
        self._charge_amps = None
        self._lcd_brightness = None
        self._error_info = None
        self._error_details = None
        self._l1_voltage = None
        self._l1_amperage = None
        self._l2_voltage = None
        self._l2_amperage = None
        self._l3_voltage = None
        self._l3_amperage = None
        self._total_energy = None
        self._current_amount = None
        self._inner_temp_c = None
        self._inner_temp_f = None
        self._outer_temp = None
        self._emergency_btn_state = None
        self._plug_state = None
        self._output_state = None
        self._current_state = None
        self._new_protocol = None
        self._current_energy = None
        self._charging_status = None
        self._charging_status_description = None
        self._charger_status = None
        self._language = None
        self._system_time = None
        self._system_time_raw = None
        self._temperature_unit = None
        self._device_name = None
        

    @property
    def info(self):
        return {
            'serial': self._serial,
            'type': self._type,
            'phases': self._phases,
            'manufacturer': self._manufacturer,
            'model': self._model,
            'hardware_version': self._hardware_version,
            'software_version': self._software_version,
            'output_power': self._output_power,
            'output_max_amps': self._output_max_amps,
            'feature': self._feature,
            'support': self._support,
            'mac': self._mac 
        }
        
    @property
    def config(self):
        return {
            'charge_amps': self._charge_amps,
            'lcd_brightness': self._lcd_brightness,
            'system_time': self._system_time,
            'system_time_raw': self._system_time_raw,
            'temperature_unit': self._temperature_unit,
            'language': self._language,
            'device_name': self._device_name,
        }
        
    @property
    def stats(self):
        return {
            'line_id': self._line_id,
            'start_user': self._start_user,
            'end_user': self._end_user,
            'charge_id': self._charge_id,
            'has_reservation': self._has_reservation,
            'start_type': self._start_type,
            'charge_type': self._charge_type,
            'charge_param1': self._charge_param1,
            'charge_param2': self._charge_param2,
            'charge_param3': self._charge_param3,
            'reason': self._reason,
            'has_stop_charge': self._has_stop_charge,
            'reservationDate': self._reservationDate,
            'start_date': self._start_date,
            'end_date': self._end_date,
            'duration': self._duration,
            'start_battery': self._start_battery,
            'end_battery': self._end_battery,
            'number': self._number,
            'charge_price': self._charge_price,
            'fee_type': self._fee_type,
            'charge_fee': self._charge_fee,
            'log_kw_length': self._log_kw_length,
            'log_kw': self._log_kw,
            'log_charge_data': self._log_charge_data,
        }
        
    @property
    def charge(self):
        return {
            'line_id': self._line_id,
            'error_info': self._error_info,
            'error_details': self._error_details,
            'l1_voltage': self._l1_voltage,
            'l1_amperage': self._l1_amperage,
            'l2_voltage': self._l2_voltage,
            'l2_amperage': self._l2_amperage,
            'l3_voltage': self._l3_voltage,
            'l3_amperage': self._l3_amperage,
            'total_energy': self._total_energy,
            'current_amount': self._current_amount,
            'inner_temp_c': self._inner_temp_c,
            'inner_temp_f': self._inner_temp_f,
            'outer_temp': self._outer_temp,
            'emergency_btn_state': self._emergency_btn_state,
            'plug_state': self._plug_state,
            'output_state': self._output_state,
            'current_state': self._current_state,
            'new_protocol': self._new_protocol,
            'current_energy': self._current_energy,
            'charging_status': self._charging_status,
            'charging_status_description': self._charging_status_description,
            'charger_status': self._charger_status
        }

    @info.setter
    def info(self, info_dict):
        for key, value in info_dict.items():
            attribute_name = f'_{key}'
            if hasattr(self, attribute_name):
                setattr(self, attribute_name, value)
                
                if key == "serial":
                    self.initialization_state = True
            else:
                raise KeyError(f"Invalid device.info key: {key}")

    @config.setter
    def config(self, config_dict):
        for key, value in config_dict.items():
            attribute_name = f'_{key}'
            if hasattr(self, attribute_name):
                setattr(self, attribute_name, value)
            else:
                raise KeyError(f"Invalid device.config key: {key}")

    @stats.setter
    def stats(self, stats_dict):
        for key, value in stats_dict.items():
            attribute_name = f'_{key}'
            if hasattr(self, attribute_name):
                setattr(self, attribute_name, value)
            else:
                raise KeyError(f"Invalid device.config key: {key}")

    @charge.setter
    def charge(self, charge_dict):
        for key, value in charge_dict.items():
            attribute_name = f'_{key}'
            if hasattr(self, attribute_name):
                setattr(self, attribute_name, value)
            else:
                raise KeyError(f"Invalid device.config key: {key}")

    def update_info(self, info_dict):
        for key, value in info_dict.items():
            attribute_name = f'_{key}'
            if hasattr(self, attribute_name):
                setattr(self, attribute_name, value)
            else:
                raise KeyError(f"Invalid device.info key: {key}")

    def __repr__(self):
        return f"<Device {self.info['model']} ({self.info['serial']})>" if self.initialization_state else f"<Device initializing>"