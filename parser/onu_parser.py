import re


def parse_onu_list(raw_output: str):
    onu_list = []
    current_onu = None

    for line in raw_output.splitlines():
        line = line.strip()

        interface_match = re.match(r"interface\s+(gpon-onu_\S+)", line)
        if interface_match:
            current_onu = {
                "interface": interface_match.group(1),
                "name": "",
                "description": ""
            }
            onu_list.append(current_onu)
            continue

        if current_onu:
            name_match = re.match(r"name\s+(.+)", line)
            if name_match:
                current_onu["name"] = name_match.group(1).strip()

            desc_match = re.match(r"description\s+(.+)", line)
            if desc_match:
                current_onu["description"] = desc_match.group(1).strip()

    return onu_list


def search_onu_by_name(raw_output: str, keyword: str):
    keyword = keyword.lower()
    onu_list = parse_onu_list(raw_output)

    results = []

    for onu in onu_list:
        name = onu.get("name", "").lower()
        description = onu.get("description", "").lower()

        if keyword in name or keyword in description:
            results.append(onu)

    return results
