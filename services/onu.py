from services.ssh_client import SSHClient
from services.onu_cache import (
    merge_onu_cache,
    search_onu_cache
)

from config.device import DEVICES

import re


def normalize_site(site):
    return site.upper().strip()


def check_onu(keyword):
    return search_onu_cache(keyword)


def get_olt_ssh(site):
    site = normalize_site(site)

    device = DEVICES.get(site)

    if not device:
        raise ValueError(
            f"Site '{site}' tidak ditemukan di config/device.py"
        )

    olt = device["olt"]

    print("================================")
    print(f"CONNECT TO OLT SITE : {site}")
    print(f"OLT HOST            : {olt['host']}")
    print(f"OLT USER            : {olt['username']}")
    print("================================")

    return SSHClient(
        host=olt["host"],
        username=olt["username"],
        password=olt["password"]
    )


def get_site_ports(site):
    site = normalize_site(site)

    device = DEVICES.get(site)

    if not device:
        raise ValueError(
            f"Site '{site}' tidak ditemukan di config/device.py"
        )

    return device["olt"].get("ports", [])


def get_onu_ids_from_olt_port(ssh, port):
    command = f"show running-config interface gpon-olt_{port}"
    result = ssh.execute(command, wait_time=8)

    onu_ids = []

    if not result:
        return onu_ids

    if result.startswith("ERROR"):
        print(result)
        return onu_ids

    for line in result.splitlines():
        line = line.strip()

        match = re.match(r"^onu\s+(\d+)\s+type", line)

        if match:
            onu_ids.append(
                int(match.group(1))
            )

    return onu_ids


def parse_onu_detail(result, interface, site):
    site = normalize_site(site)

    onu = {
        "site": site,
        "interface": interface,
        "pon": "-",
        "onu_id": "-",
        "name": "-",
        "description": "-"
    }

    match = re.match(
        r"gpon-onu_(\d+/\d+/\d+):(\d+)",
        interface
    )

    if match:
        onu["pon"] = match.group(1)
        onu["onu_id"] = match.group(2)

    for line in result.splitlines():
        line = line.strip()

        if line.startswith("name "):
            onu["name"] = (
                line.replace("name ", "")
                .strip()
            )

        elif line.startswith("description "):
            onu["description"] = (
                line.replace("description ", "")
                .strip()
            )

    return onu


def refresh_onu_cache(site, target_port=None):
    site = normalize_site(site)

    ssh = get_olt_ssh(site)

    if target_port:
        ports_to_scan = [
            target_port.strip()
        ]
    else:
        ports_to_scan = get_site_ports(site)

    if not ports_to_scan:
        raise ValueError(
            f"Port untuk site '{site}' belum dikonfigurasi."
        )

    onu_data = []
    refreshed_ports = []

    for port in ports_to_scan:
        print(f"SCAN SITE: {site} | PORT: {port}")

        onu_ids = get_onu_ids_from_olt_port(
            ssh,
            port
        )

        refreshed_ports.append(port)

        print(
            f"TOTAL ONU FOUND ON {site} {port}: {len(onu_ids)}"
        )

        for onu_id in onu_ids:
            interface = f"gpon-onu_{port}:{onu_id}"
            command = f"show running-config interface {interface}"

            result = ssh.execute(
                command,
                wait_time=5
            )

            if not result:
                continue

            if result.startswith("ERROR"):
                print(result)
                continue

            expected_interface_line = f"interface {interface}"

            if expected_interface_line not in result:
                print(
                    f"SKIP INVALID ONU: {site} {interface}"
                )
                continue

            onu = parse_onu_detail(
                result,
                interface,
                site
            )

            if (
                onu["name"] == "-"
                and onu["description"] == "-"
            ):
                print(
                    f"SKIP EMPTY ONU: {site} {interface}"
                )
                continue

            onu_data.append(onu)

            print(
                f"FOUND ONU: {site} | {onu['interface']} | {onu['name']}"
            )

    summary = merge_onu_cache(
        onu_data,
        site,
        refreshed_ports
    )

    return summary
