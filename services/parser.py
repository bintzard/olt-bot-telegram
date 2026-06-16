def clean_output(output):

    lines = output.splitlines()

    cleaned = []

    blacklist = [

        "SELAMAT DATANG",
        "Last login time",
        "The password is not strong",
        "*************************************************************************",
        "",
    ]

    for line in lines:

        skip = False

        for bad in blacklist:

            if bad in line:

                skip = True

        if not skip:

            cleaned.append(line)

    return "\n".join(cleaned)
