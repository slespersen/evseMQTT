import json
from .constants import Constants

class MQTTPayloads:
    def __init__(self, device):
        self.device = device
        
        self.base_device = {
            "device": {
                "identifiers": [self.device.info['mac']],
                "name": f"{self.device.info['manufacturer']} {self.device.info['model']}", # Should be using the advertised name "ACP#<name>" 
                "manufacturer": self.device.info['manufacturer'],
                "model": self.device.info['model'],
                "connections": [["mac", self.device.info['mac']]],
                "serial_number": self.device.info['serial'],
                "sw_version": str(self.device.info['software_version'])
            }
        }
        
        self.entities = {
            "charge": {
                "name": "Charge",
                "device_class": "switch",
                "icon": "mdi:ev-plug-type2",
                "unique_id": f"{self.device.info['serial']}",
                "state_topic": f"evseMQTT/{self.device.info['serial']}/state/charge",
                "command_topic": f"evseMQTT/{self.device.info['serial']}/command",
                "availability_topic": f"evseMQTT/{self.device.info['serial']}/availability",
                "payload_available": "online",
                "payload_not_available": "offline",
                "payload_on": 1,
                "payload_off": 0,
                "command_template": "{\"charge_state\": {{ value }} }",
                "value_template": "{{ value_json.charger_status }}",
            },
            "error_state": {
                "name": "Error State",
                "device_class": "enum",
                "device_type": "sensor",
                "unique_id": f"{self.device.info['serial']}",
                "state_topic": f"evseMQTT/{self.device.info['serial']}/state/charge",
                "availability_topic": f"evseMQTT/{self.device.info['serial']}/availability",
                "payload_available": "online",
                "payload_not_available": "offline",
                "options": list(set(Constants.ERRORS.values())),
                "value_template": "{{ value_json.error_details }}",
                "entity_category": "diagnostic"
            },
            "charging_status": {
                "name": "Status",
                "device_class": "enum",
                "device_type": "sensor",
                "unique_id": f"{self.device.info['serial']}",
                "state_topic": f"evseMQTT/{self.device.info['serial']}/state/charge",
                "availability_topic": f"evseMQTT/{self.device.info['serial']}/availability",
                "payload_available": "online",
                "payload_not_available": "offline",
                "options": list(set(Constants.CHARGING_STATUS.values())),
                "value_template": "{{ value_json.charging_status }}",
                "entity_category": "diagnostic"
            },
            "charging_status_description": {
                "name": "Message",
                "device_class": "enum",
                "device_type": "sensor",
                "unique_id": f"{self.device.info['serial']}",
                "state_topic": f"evseMQTT/{self.device.info['serial']}/state/charge",
                "availability_topic": f"evseMQTT/{self.device.info['serial']}/availability",
                "payload_available": "online",
                "payload_not_available": "offline",
                "options": list(set(Constants.CHARGING_STATUS_DESCRIPTIONS.values())),
                "value_template": "{{ value_json.charging_status_description }}",
            },
            "current_state": {
                "name": "Current State",
                "device_class": "enum",
                "device_type": "sensor",
                "unique_id": f"{self.device.info['serial']}",
                "state_topic": f"evseMQTT/{self.device.info['serial']}/state/charge",
                "availability_topic": f"evseMQTT/{self.device.info['serial']}/availability",
                "payload_available": "online",
                "payload_not_available": "offline",
                "options": Constants.CURRENT_STATE,
                "value_template": "{{ value_json.current_state }}",
            },
            "plug_state": {
                "name": "Plug State",
                "device_class": "enum",
                "device_type": "sensor",
                "unique_id": f"{self.device.info['serial']}",
                "state_topic": f"evseMQTT/{self.device.info['serial']}/state/charge",
                "availability_topic": f"evseMQTT/{self.device.info['serial']}/availability",
                "payload_available": "online",
                "payload_not_available": "offline",
                "options": Constants.PLUG_STATE,
                "value_template": "{{ value_json.plug_state }}",
                "entity_category": "diagnostic"
            },
            "output_state": {
                "name": "Output State",
                "device_class": "enum",
                "device_type": "sensor",
                "unique_id": f"{self.device.info['serial']}",
                "state_topic": f"evseMQTT/{self.device.info['serial']}/state/charge",
                "availability_topic": f"evseMQTT/{self.device.info['serial']}/availability",
                "payload_available": "online",
                "payload_not_available": "offline",
                "options": Constants.OUTPUT_STATE,
                "value_template": "{{ value_json.output_state }}",
                "entity_category": "diagnostic"
            },
            "device_date": {
                "name": "Date",
                "icon": "mdi:calendar-month-outline",
                "unique_id": f"{self.device.info['serial']}",
                "enabled_by_default": False,
                "state_topic": f"evseMQTT/{self.device.info['serial']}/state/config",
                "availability_topic": f"evseMQTT/{self.device.info['serial']}/availability",
                "value_template": "{{ value_json.system_time_raw | int | timestamp_custom('%Y-%m-%d', true) }}",
                "entity_category": "diagnostic"
            },
            "device_time": {
                "name": "Time",
                "icon": "mdi:clock-outline",
                "unique_id": f"{self.device.info['serial']}",
                "enabled_by_default": False,
                "state_topic": f"evseMQTT/{self.device.info['serial']}/state/config",
                "availability_topic": f"evseMQTT/{self.device.info['serial']}/availability",
                "value_template": "{{ value_json.system_time_raw | int | timestamp_custom('%H:%M', true) }}",
                "entity_category": "diagnostic"
            },
            "total_energy": {
                "name": "Total Energy",
                "device_class": "energy",
                "device_type": "sensor",
                "unique_id": f"{self.device.info['serial']}",
                "state_topic": f"evseMQTT/{self.device.info['serial']}/state/charge",
                "availability_topic": f"evseMQTT/{self.device.info['serial']}/availability",
                "payload_available": "online",
                "payload_not_available": "offline",
                "unit_of_measurement": "kWh",
                "state_class": "total_increasing",
                "value_template": "{{ value_json.current_amount }}",
                "entity_category": "diagnostic"
            },
            "current_energy": {
                "name": "Current Energy",
                "device_class": "power",
                "device_type": "sensor",
                "unique_id": f"{self.device.info['serial']}",
                "state_topic": f"evseMQTT/{self.device.info['serial']}/state/charge",
                "availability_topic": f"evseMQTT/{self.device.info['serial']}/availability",
                "payload_available": "online",
                "payload_not_available": "offline",
                "unit_of_measurement": "W" if self.device.unit == "W" else "kW",
                "state_class": "measurement",
                "value_template": "{{ value_json.current_energy }}",
                "entity_category": "diagnostic"
            },
            "device_name": {
                "name": "Name",
                "device_type": "text",
                "unique_id": f"{self.device.info['serial']}",
                "state_topic": f"evseMQTT/{self.device.info['serial']}/state/config",
                "availability_topic": f"evseMQTT/{self.device.info['serial']}/availability",
                "command_topic": f"evseMQTT/{self.device.info['serial']}/command",
                "payload_available": "online",
                "payload_not_available": "offline",
                "command_template": "{\"device_name\": \"{{ value }}\" }",
                "min": 1,
                "max": 11,
                "value_template": "{% if value_json.device_name is defined %}{{ value_json.device_name }}{% endif %}",
                "entity_category": "config"
            },
            "temperature_c": {
                "name": "Temperature",
                "device_class": "temperature",
                "device_type": "sensor",
                "enabled_by_default": True if self.device.config['temperature_unit'] == "Celcius" else False,
                "unique_id": f"{self.device.info['serial']}",
                "state_topic": f"evseMQTT/{self.device.info['serial']}/state/charge",
                "availability_topic": f"evseMQTT/{self.device.info['serial']}/availability",
                "payload_available": "online",
                "payload_not_available": "offline",
                "unit_of_measurement": "°C",
                "state_class": "measurement",
                "value_template": "{{ value_json.inner_temp_c }}",
                "entity_category": "diagnostic"
            },
            "temperature_f": {
                "name": "Temperature",
                "device_class": "temperature",
                "device_type": "sensor",
                "enabled_by_default": True if self.device.config['temperature_unit'] == "Fahrenheit" else False,
                "unique_id": f"{self.device.info['serial']}",
                "state_topic": f"evseMQTT/{self.device.info['serial']}/state/charge",
                "availability_topic": f"evseMQTT/{self.device.info['serial']}/availability",
                "payload_available": "online",
                "payload_not_available": "offline",
                "unit_of_measurement": "°F",
                "state_class": "measurement",
                "value_template": "{{ value_json.inner_temp_f }}",
                "entity_category": "diagnostic"
            },
            "language": {
                "name": "Language",
                "device_class": "select",
                "icon": "mdi:translate",
                "unique_id": f"{self.device.info['serial']}",                
                "state_topic": f"evseMQTT/{self.device.info['serial']}/state/config",
                "availability_topic": f"evseMQTT/{self.device.info['serial']}/availability",
                "command_topic": f"evseMQTT/{self.device.info['serial']}/command",
                "payload_available": "online",
                "payload_not_available": "offline",
                "options": list(Constants.LANGUAGES.keys()),
                "command_template": "{\"language\": \"{{ value }}\" }",
                "value_template": "{{ value_json.language }}",
                "entity_category": "config"
            },
            "temperature_unit": {
                "name": "Temperature Unit",
                "device_class": "select",
                "icon": "mdi:thermometer",
                "unique_id": f"{self.device.info['serial']}",                
                "state_topic": f"evseMQTT/{self.device.info['serial']}/state/config",
                "availability_topic": f"evseMQTT/{self.device.info['serial']}/availability",
                "command_topic": f"evseMQTT/{self.device.info['serial']}/command",
                "payload_available": "online",
                "payload_not_available": "offline",
                "options": list(Constants.TEMPERATURE_UNIT.keys()),
                "command_template": "{\"temperature_unit\": \"{{ value }}\" }",
                "value_template": "{{ value_json.temperature_unit }}",
                "entity_category": "config"
            },
            "lcd_brightness": {
                "name": "LCD Brightness",
                "device_type": "number",
                "icon": "mdi:brightness-percent",
                "enabled_by_default": False,
                "unique_id": f"{self.device.info['serial']}",
                "state_topic": f"evseMQTT/{self.device.info['serial']}/state/config",
                "availability_topic": f"evseMQTT/{self.device.info['serial']}/availability",
                "command_topic": f"evseMQTT/{self.device.info['serial']}/command",
                "payload_available": "online",
                "payload_not_available": "offline",
                "unit_of_measurement": "percent",
                "min": 1, 
                "max": 100, 
                "step": 1, 
                "command_template": "{\"lcd_brightness\": {{ value }} }",
                "value_template": "{{ value_json.lcd_brightness }}",
                "entity_category": "config"
            },
            "charge_amps": {
                "name": "Charge Amps",
                "device_type": "number",
                "icon": "mdi:current-ac",
                "unique_id": f"{self.device.info['serial']}",
                "state_topic": f"evseMQTT/{self.device.info['serial']}/state/config",
                "availability_topic": f"evseMQTT/{self.device.info['serial']}/availability",
                "command_topic": f"evseMQTT/{self.device.info['serial']}/command",
                "payload_available": "online",
                "payload_not_available": "offline",
                "unit_of_measurement": "A",
                "min": 6, 
                "max": self.device.info['output_max_amps'], 
                "step": 1, 
                "command_template": "{\"charge_amps\": {{ value }} }",
                "value_template": "{{ value_json.charge_amps }}",
            },
            "charge_amps_sensor": {
                "name": "Charge Amps",
                "device_class": "current",
                "device_type": "sensor",
                "icon": "mdi:current-ac",
                "unique_id": f"{self.device.info['serial']}",
                "state_topic": f"evseMQTT/{self.device.info['serial']}/state/config",
                "availability_topic": f"evseMQTT/{self.device.info['serial']}/availability",
                "payload_available": "online",
                "payload_not_available": "offline",
                "unit_of_measurement": "A",
                "value_template": "{{ value_json.charge_amps }}",
            },
            "l1_voltage": {
                "name": "L1 Voltage",
                "device_class": "voltage",
                "device_type": "sensor",
                "unique_id": f"{self.device.info['serial']}",
                "state_topic": f"evseMQTT/{self.device.info['serial']}/state/charge",
                "availability_topic": f"evseMQTT/{self.device.info['serial']}/availability",
                "payload_available": "online",
                "payload_not_available": "offline",
                "unit_of_measurement": "V",
                "state_class": "measurement",
                "value_template": "{{ value_json.l1_voltage }}",
                "entity_category": "diagnostic"
            },
            "l1_amps": {
                "name": "L1 Amperage",
                "device_class": "current",
                "device_type": "sensor",
                "unique_id": f"{self.device.info['serial']}",
                "state_topic": f"evseMQTT/{self.device.info['serial']}/state/charge",
                "availability_topic": f"evseMQTT/{self.device.info['serial']}/availability",
                "payload_available": "online",
                "payload_not_available": "offline",
                "unit_of_measurement": "A",
                "state_class": "measurement",
                "value_template": "{{ value_json.l1_amperage }}",
                "entity_category": "diagnostic"
            },
        }
        
        self.phase_entities = {
            "l2_voltage": {
                "name": "L2 Voltage",
                "device_class": "voltage",
                "device_type": "sensor",
                "unique_id": f"{self.device.info['serial']}",
                "state_topic": f"evseMQTT/{self.device.info['serial']}/state/charge",
                "availability_topic": f"evseMQTT/{self.device.info['serial']}/availability",
                "payload_available": "online",
                "payload_not_available": "offline",
                "unit_of_measurement": "V",
                "state_class": "measurement",
                "value_template": "{{ value_json.l2_voltage }}",
                "entity_category": "diagnostic"
            },
            "l2_amps": {
                "name": "L2 Amperage",
                "device_class": "current",
                "device_type": "sensor",
                "unique_id": f"{self.device.info['serial']}",
                "state_topic": f"evseMQTT/{self.device.info['serial']}/state/charge",
                "availability_topic": f"evseMQTT/{self.device.info['serial']}/availability",
                "payload_available": "online",
                "payload_not_available": "offline",
                "unit_of_measurement": "A",
                "state_class": "measurement",
                "value_template": "{{ value_json.l2_amperage }}",
                "entity_category": "diagnostic"
            },
            "l3_voltage": {
                "name": "L3 Voltage",
                "device_class": "voltage",
                "device_type": "sensor",
                "unique_id": f"{self.device.info['serial']}",
                "state_topic": f"evseMQTT/{self.device.info['serial']}/state/charge",
                "availability_topic": f"evseMQTT/{self.device.info['serial']}/availability",
                "payload_available": "online",
                "payload_not_available": "offline",
                "unit_of_measurement": "V",
                "state_class": "measurement",
                "value_template": "{{ value_json.l3_voltage }}",
                "entity_category": "diagnostic"
            },
            "l3_amps": {
                "name": "L3 Amperage",
                "device_class": "current",
                "device_type": "sensor",
                "unique_id": f"{self.device.info['serial']}",
                "state_topic": f"evseMQTT/{self.device.info['serial']}/state/charge",
                "availability_topic": f"evseMQTT/{self.device.info['serial']}/availability",
                "payload_available": "online",
                "payload_not_available": "offline",
                "unit_of_measurement": "A",
                "state_class": "measurement",
                "value_template": "{{ value_json.l3_amperage }}",
                "entity_category": "diagnostic"
            },
        }
        
        if self.device.info['phases'] == 3:
            self.entities.update(self.phase_entities)

    def discovery(self):  
        discovery_entities = []
        
        for entity, data in self.entities.items():
            
            if "device_class" in data:
                device_class = data['device_class']
            
            if "device_type" in data:
                device_class = data['device_type']
                data.pop('device_type')
            
            temp_entity = {}
            temp_entity.update(data)
            temp_entity.update({"unique_id": f"{data['unique_id']}_{entity}"})
            temp_entity.update({"config_topic": f"homeassistant/{device_class}/{data['unique_id']}/{entity}/config"})
            temp_entity.update(self.base_device)
            
            discovery_entities.append(temp_entity)
    
        return discovery_entities