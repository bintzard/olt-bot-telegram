import json
import os


SECURITY_FILE = "data/allowed_users.json"


def load_security_data():
    if not os.path.exists(SECURITY_FILE):
        return {
            "owner_id": 0,
            "allowed_users": [],
            "refresh_admins": []
        }

    with open(SECURITY_FILE, "r") as file:
        return json.load(file)


def save_security_data(data):
    os.makedirs("data", exist_ok=True)

    with open(SECURITY_FILE, "w") as file:
        json.dump(data, file, indent=4)


def is_user_allowed(user_id):
    data = load_security_data()

    return (
        user_id == data.get("owner_id")
        or user_id in data.get("allowed_users", [])
    )


def is_owner(user_id):
    data = load_security_data()

    return user_id == data.get("owner_id")


def can_refresh(user_id):
    data = load_security_data()

    return (
        user_id == data.get("owner_id")
        or user_id in data.get("refresh_admins", [])
    )


async def deny_access(update):
    await update.message.reply_text(
        "⛔ Akses ditolak.\n"
        "Anda tidak memiliki izin menggunakan bot ini."
    )
