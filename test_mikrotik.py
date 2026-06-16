import os
from dotenv import load_dotenv
import routeros_api


load_dotenv()


MIKROTIK_HOST = os.getenv("MIKROTIK_HOST")
MIKROTIK_USER = os.getenv("MIKROTIK_USER")
MIKROTIK_PASS = os.getenv("MIKROTIK_PASS")
MIKROTIK_PORT = int(os.getenv("MIKROTIK_PORT", 8728))


connection = routeros_api.RouterOsApiPool(
    MIKROTIK_HOST,
    username=MIKROTIK_USER,
    password=MIKROTIK_PASS,
    port=MIKROTIK_PORT,
    plaintext_login=True
)

api = connection.get_api()

ppp_active = api.get_resource("/ppp/active")
users = ppp_active.get()

print("TOTAL PPPoE ACTIVE:", len(users))

for user in users[:10]:
    print(user)

connection.disconnect()
