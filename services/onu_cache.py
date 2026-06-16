import json
import os
from datetime import datetime


CACHE_FILE = "data/onu_cache.json"


def build_summary(data):
    sites = {}

    for onu in data:
        site = onu.get("site", "UNKNOWN")
        pon = onu.get("pon", "-")

        if site not in sites:
            sites[site] = {
                "total_onu": 0,
                "ports": {}
            }

        sites[site]["total_onu"] += 1

        if pon not in sites[site]["ports"]:
            sites[site]["ports"][pon] = 0

        sites[site]["ports"][pon] += 1

    total_pon = 0

    for site_data in sites.values():
        total_pon += len(site_data["ports"])

    return {
        "last_refresh": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_site": len(sites),
        "total_pon": total_pon,
        "total_onu": len(data),
        "sites": sites
    }


def save_onu_cache(data):
    os.makedirs("data", exist_ok=True)

    cache = {
        "summary": build_summary(data),
        "data": data
    }

    with open(CACHE_FILE, "w") as file:
        json.dump(cache, file, indent=4)


def load_onu_cache():
    if not os.path.exists(CACHE_FILE):
        return {
            "summary": {},
            "data": []
        }

    with open(CACHE_FILE, "r") as file:
        return json.load(file)


def merge_onu_cache(new_data, site, refreshed_ports):
    cache = load_onu_cache()
    old_data = cache.get("data", [])

    filtered_old_data = [
        onu for onu in old_data
        if not (
            onu.get("site") == site
            and onu.get("pon") in refreshed_ports
        )
    ]

    merged_data = filtered_old_data + new_data

    save_onu_cache(merged_data)

    return build_summary(merged_data)


def normalize_text(text):
    return (
        text.lower()
        .replace(" ", "")
        .replace("_", "")
        .replace("-", "")
    )


def remove_prefix_number(text):
    return text.lstrip("0123456789")


def search_onu_cache(keyword):
    cache = load_onu_cache()
    data = cache.get("data", [])

    keyword_normalized = normalize_text(keyword)

    results = []

    for onu in data:
        name_raw = normalize_text(
            onu.get("name", "")
        )

        name = remove_prefix_number(name_raw)

        description = normalize_text(
            onu.get("description", "")
        )

        interface = normalize_text(
            onu.get("interface", "")
        )

        site = normalize_text(
            onu.get("site", "")
        )

        if (
            name.startswith(keyword_normalized)
            or description.startswith(keyword_normalized)
            or keyword_normalized in interface
            or keyword_normalized == site
        ):
            results.append(onu)

    return results


def get_onu_cache_summary():
    cache = load_onu_cache()
    return cache.get("summary", {})
