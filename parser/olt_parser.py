def clean_output(output):

    lines = output.splitlines()

    result = []

    start_parse = False

    for line in lines:

        line = line.strip()

        if not line:
            continue

        # mulai parsing setelah header
        if "Rack Shelf Slot" in line:

            start_parse = True
            continue

        # skip garis
        if "-----" in line:
            continue

        # skip banner
        if (
            "SELAMAT DATANG" in line
            or "Last login time" in line
            or "password is not strong" in line
            or "OLT-BALEN#" in line
        ):
            continue

        if start_parse:

            parts = line.split()

            # pastikan format valid
            if len(parts) >= 9:

                slot = parts[2]

                real_type = parts[4]

                port = parts[5]

                status = parts[-1]

                icon = "🟢"

                if status != "INSERVICE":

                    icon = "🔴"

                card_info = (
                    f"{icon} SLOT {slot}\n"
                    f"┣ Type : {real_type}\n"
                    f"┣ Port : {port}\n"
                    f"┗ Status : {status}\n"
                )

                result.append(card_info)

    if not result:

        return "No card information found"

    final_output = "📦 STATUS CARD OLT\n\n"

    final_output += "\n".join(result)

    return final_output
