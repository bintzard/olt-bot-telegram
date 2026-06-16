import json
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

    total_pon = sum(
        len(site_data["ports"])
        for site_data in sites.values()
    )

    return {
        "last_refresh": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_site": len(sites),
        "total_pon": total_pon,
        "total_onu": len(data),
        "sites": sites
    }


with open(CACHE_FILE, "r") as file:
    cache = json.load(file)

old_data = cache.get("data", [])

new_data = [
    onu for onu in old_data
    if onu.get("site") not in [None, "", "UNKNOWN"]
]

new_cache = {
    "summary": build_summary(new_data),
    "data": new_data
}

with open(CACHE_FILE, "w") as file:
    json.dump(new_cache, file, indent=4)

print(f"Data lama: {len(old_data)}")
print(f"Data baru: {len(new_data)}")
print(f"Data UNKNOWN dihapus: {len(old_data) - len(new_data)}")
