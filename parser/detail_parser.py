def get_value(line):
    return line.split(":", 1)[1].strip()


def parse_onu_detail(raw_output):
    data = {
        "interface": "-",
        "name": "-",
        "type": "-",
        "state": "-",
        "phase_state": "-",
        "admin_state": "-",
        "config_state": "-",
        "serial_number": "-",
        "description": "-",
        "onu_distance": "-",
        "online_duration": "-",
        "last_offline_time": "-",
        "last_down_cause": "-"
    }

    for line in raw_output.splitlines():
        line = line.strip()

        if line.startswith("ONU interface:"):
            data["interface"] = get_value(line)

        elif line.startswith("Name:"):
            data["name"] = get_value(line)

        elif line.startswith("Type:"):
            data["type"] = get_value(line)

        elif line.startswith("State:"):
            data["state"] = get_value(line)

        elif line.startswith("Phase state:"):
            data["phase_state"] = get_value(line)

        elif line.startswith("Admin state:"):
            data["admin_state"] = get_value(line)

        elif line.startswith("Config state:"):
            data["config_state"] = get_value(line)

        elif line.startswith("Serial number:"):
            data["serial_number"] = get_value(line)

        elif line.startswith("Description:"):
            data["description"] = get_value(line)

        elif line.startswith("ONU Distance:"):
            data["onu_distance"] = get_value(line)

        elif line.startswith("Online Duration:"):
            data["online_duration"] = get_value(line)

    return data
