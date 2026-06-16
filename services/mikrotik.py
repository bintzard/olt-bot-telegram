import routeros_api

from config.device import DEVICES


def normalize_text(text):
    return (
        text.lower()
        .replace(" ", "")
        .replace("_", "")
        .replace("-", "")
        .strip()
    )


def is_pon_id_keyword(keyword):
    """
    Deteksi keyword berbentuk PON:ID.
    Contoh:
    1/2/3:4
    1/2/3:43
    """
    return "/" in keyword and ":" in keyword


def is_exact_pon_id_match(username, keyword):
    """
    Cocokkan PPPoE berdasarkan PON:ID secara ketat.

    Benar:
    keyword 1/2/3:4 cocok dengan 1/2/3:4_cakmol

    Salah:
    keyword 1/2/3:4 tidak boleh cocok dengan 1/2/3:43_muhammad
    """
    username = username.lower().strip()
    keyword = keyword.lower().strip()

    return (
        username == keyword
        or username.startswith(f"{keyword}_")
        or username.startswith(f"{keyword}-")
        or username.startswith(f"{keyword}.")
    )


def mikrotik_api(site):
    site = site.upper()

    device = DEVICES.get(site)

    if not device:
        raise ValueError(f"Site '{site}' tidak ditemukan di config/device.py")

    mikrotik = device["mikrotik"]

    connection = routeros_api.RouterOsApiPool(
        mikrotik["host"],
        username=mikrotik["username"],
        password=mikrotik["password"],
        port=mikrotik.get("port", 8728),
        plaintext_login=True
    )

    return connection


def format_active_user(user):
    return {
        "username": user.get("name", "-"),
        "ip": user.get("address", "-"),
        "uptime": user.get("uptime", "-"),
        "service": user.get("service", "-"),
        "status": "active"
    }


def format_secret_user(user):
    return {
        "username": user.get("name", "-"),
        "ip": "-",
        "uptime": "-",
        "service": user.get("service", "-"),
        "last_logged_out": user.get("last-logged-out", "-"),
        "status": "offline"
    }


def get_pppoe_active_exact(site, username):
    connection = None

    try:
        connection = mikrotik_api(site)
        api = connection.get_api()

        ppp_active = api.get_resource("/ppp/active")
        result = ppp_active.get(name=username)

        if not result:
            return None

        return format_active_user(result[0])

    except Exception as e:
        print(f"MIKROTIK ACTIVE EXACT ERROR [{site}]: {e}")
        return None

    finally:
        if connection:
            connection.disconnect()


def search_pppoe_active(site, keyword):
    connection = None

    try:
        connection = mikrotik_api(site)
        api = connection.get_api()

        ppp_active = api.get_resource("/ppp/active")
        users = ppp_active.get()

        keyword_normalized = normalize_text(keyword)
        is_pon_search = is_pon_id_keyword(keyword)

        for user in users:
            username = user.get("name", "")
            username_normalized = normalize_text(username)

            # Kalau keyword adalah PON:ID,
            # wajib cocok secara ketat.
            # Contoh 1/2/3:4 hanya cocok ke 1/2/3:4_xxx,
            # tidak boleh cocok ke 1/2/3:43_xxx.
            if is_pon_search:
                if is_exact_pon_id_match(username, keyword):
                    return format_active_user(user)

            # Kalau keyword bukan PON:ID,
            # baru boleh pakai pencarian contains biasa.
            else:
                if keyword_normalized in username_normalized:
                    return format_active_user(user)

        return None

    except Exception as e:
        print(f"MIKROTIK ACTIVE SEARCH ERROR [{site}]: {e}")
        return None

    finally:
        if connection:
            connection.disconnect()


def get_pppoe_secret_exact(site, username):
    connection = None

    try:
        connection = mikrotik_api(site)
        api = connection.get_api()

        ppp_secret = api.get_resource("/ppp/secret")
        result = ppp_secret.get(name=username)

        if not result:
            return None

        return format_secret_user(result[0])

    except Exception as e:
        print(f"MIKROTIK SECRET EXACT ERROR [{site}]: {e}")
        return None

    finally:
        if connection:
            connection.disconnect()


def search_pppoe_secret(site, keyword):
    connection = None

    try:
        connection = mikrotik_api(site)
        api = connection.get_api()

        ppp_secret = api.get_resource("/ppp/secret")
        users = ppp_secret.get()

        keyword_normalized = normalize_text(keyword)
        is_pon_search = is_pon_id_keyword(keyword)

        for user in users:
            username = user.get("name", "")
            username_normalized = normalize_text(username)

            # Kalau keyword adalah PON:ID,
            # wajib cocok secara ketat.
            if is_pon_search:
                if is_exact_pon_id_match(username, keyword):
                    return format_secret_user(user)

            # Kalau keyword bukan PON:ID,
            # boleh contains biasa.
            else:
                if keyword_normalized in username_normalized:
                    return format_secret_user(user)

        return None

    except Exception as e:
        print(f"MIKROTIK SECRET SEARCH ERROR [{site}]: {e}")
        return None

    finally:
        if connection:
            connection.disconnect()


def get_pppoe_info(site, username):
    # 1. exact active
    active = get_pppoe_active_exact(site, username)

    if active:
        return active

    # 2. search active
    # Kalau username berbentuk PON:ID, pencarian di sini sudah ketat.
    active_search = search_pppoe_active(site, username)

    if active_search:
        return active_search

    # 3. exact secret
    secret = get_pppoe_secret_exact(site, username)

    if secret:
        return secret

    # 4. search secret
    # Kalau username berbentuk PON:ID, pencarian di sini juga sudah ketat.
    secret_search = search_pppoe_secret(site, username)

    if secret_search:
        return secret_search

    return None
