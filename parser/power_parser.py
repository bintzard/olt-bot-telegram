import re


def parse_power_output(raw_output):
    data = {
        "olt_rx": "-",
        "onu_tx": "-",
        "up_attenuation": "-",
        "olt_tx": "-",
        "onu_rx": "-",
        "down_attenuation": "-"
    }

    for line in raw_output.splitlines():
        line = line.strip()

        if line.startswith("up"):
            match = re.search(
                r"Rx\s*:\s*([-\d.]+).*Tx\s*:\s*([-\d.]+).*?([-\d.]+)\(dB\)",
                line
            )

            if match:
                data["olt_rx"] = match.group(1)
                data["onu_tx"] = match.group(2)
                data["up_attenuation"] = match.group(3)

        elif line.startswith("down"):
            match = re.search(
                r"Tx\s*:\s*([-\d.]+).*Rx\s*:\s*([-\d.]+).*?([-\d.]+)\(dB\)",
                line
            )

            if match:
                data["olt_tx"] = match.group(1)
                data["onu_rx"] = match.group(2)
                data["down_attenuation"] = match.group(3)

    return data
