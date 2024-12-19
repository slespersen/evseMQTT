class Constants:
    # BLE UUIDs
    WRITE_UUID = "0000fff2-0000-1000-8000-00805f9b34fb"
    READ_UUID = "0000fff1-0000-1000-8000-00805f9b34fb"
    
    ERRORS = {
        0: "Relay Stick Error",
        1: "Relay Stick Error",
        2: "Relay Stick Error",
        3: "OFFLINE",
        4: "CC Error",
        5: "CP Error",
        6: "Emergency Stop",
        7: "Over Temperature",
        8: "Over Temperature",
        9: "Unknown",
        10: "Leakage Protection",
        11: "Short Circuit",
        12: "Over Current",
        13: "Ungrounded",
        14: "Over Voltage",
        15: "Low Voltage",
        25: "Input Power Error",
        26: "DLB Over Current - Mains overload",
        27: "Diode Short Circuit",
        28: "RTC Failure",
        29: "Flash Memory Failure",
        30: "EEPROM Failure",
        31: "Metering Module Failure",
        255: "No Error"
    }
    
    PLUG_STATE = [
        "Unknown 0",
        "Disconnected",
        "Connected Unlocked",
        "Unknown 1",
        "Connected Locked",
        "Unknown 2",
        "Unknown 3",
        "Unknown 4",
        "Unknown 5",
    ]

    OUTPUT_STATE = [
        "Unknown 0",
        "Charging",
        "Idle",
        "Unknown 1",
        "Unknown 2",
        "Unknown 3",
        "Unknown 4",
        "Unknown 5",
        "Unknown 6",
    ]

    CURRENT_STATE = [
        "Fault",
        "Charging Fault 1",
        "Charging Fault 2",
        "Unknown 1",
        "Unknown 2",
        "Unknown 3",
        "Unknown 4",
        "Unknown 5",
        "Unknown 6",
        "Waiting for swipe",
        "waiting for button",
        "Not Connected",
        "Ready to charge",
        "Charging",
        "Completed",
        "Unknown 7",
        "Completed Full Charge",
        "Unknown 8",
        "Unknown 9",
        "Charging Reservation",
        "Unknown 10",
    ]
    
    CHARGING_STATUS = {
        1: "Start",
        2: "Finish Charging",
        3: "Waiting",
        4: "Finished",
        5: "Finished",
        6: "Cancel",
        7: "Connect",
        8: "Fault",
        9: "Start",
        10: "Start",
        11: "Finish Charging",
    }
    
    CHARGING_STATUS_DESCRIPTIONS = {
        1: "EV is connected, please press start",
        2: "Charging",
        3: "Charging has started, waiting for EV.",
        4: "Charging completed",
        5: "Charging completed",
        6: "Charging reservation.",
        7: "The plug is not connected, please start charging after connecting.",
        8: "See Error State",
        9: "Wait for the swipe to start",
        10: "Wait for the button to activate",
        11: "See Error State",
    }
    
    CHARGER_STATUS = {
        1: 0,
        2: 1,
        3: 1,
        4: 0,
        5: 0,
        6: 0,
        7: 0,
        8: 0,
        9: 0,
        10: 0,
        11: 0,
    }
    
    TEMPERATURE_UNIT = {
        "Celcius": 1,
        "Fahrenheit": 2
    }
    
    LANGUAGES = {
        "English": 1,
        "Italiano": 2,
        "Deutsch": 3,
        "Français": 4,
        "Español": 5,
        "עברית": 6,
        "Polski": 7,
        "中文": 8 #?! That's a pretty big if
    }
    
    # Actually used for charge records, but let's see -- we'll use it for charge_stop
    STOP_REASON = {
        0: "The reservation was stopped in advance by app",
        1: "When the appointment time arrived, there was no rush",
        11: "App stop",
        12: "Card swiping stop",
        13: "Auto fill",
        14: "Fixed fee to",
        15: "Quantitative to",
        16: "Timed to",
        17: "Draw a gun",
        18: "End of power failure (it does not support continuous charging after power failure, or it supports continuous charging, but the gun is gone after power on)",
        19: "Fault, overcurrent",
        20: "Fault, short circuit",
        21: "Fault, main board over temperature",
        22: "Fault, over temperature of plug",
        23: "Fault, emergency stop pressed",
        24: "Key end",
        30: "Exceeding the maximum time of 48H",
        31: "Exceeding the maximum power of 400kwh",
        32: "Exceeding the maximum cost of 400 yuan"
    }

    # Response to charge_start
    CHARGE_START_ERROR = {
        0: "No error",
        1: "The charging plug is not plugged in properly",
        2: "System error",
        3: "Charging",
        4: "System maintenance",
        5: "Incorrect set fee",
        6: "Incorrect set power consumption",
        7: "Incorrect set time",
        8: "Unknown reason",
        20: "Failed to start, already in reservation status",
    }

    # Response to charge_start
    CHARGE_START_RESERVATION = {
        0: "No error",
        2: "Reservation failed, the system does not support reservation",
        3: "Reservation failed, the reservation time is more than 24 hours",
        4: "Reservation failed, the reservation time is earlier than the current time",
        5: "Reservation failed, system error",
        6: "Reservation failed, already in reservation status",
        7: "Reservation failed, already in charging status",
        8: "Reservation failed, the fixed fee is incorrect",
        9: "Reservation failed, the fixed power consumption is incorrect",
        10: "Reservation failed, the fixed time is incorrect",
    }