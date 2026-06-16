# OLT Monitoring Telegram Bot

Bot Telegram untuk membantu monitoring OLT ZTE C320 dan data pelanggan PPPoE MikroTik.

Bot ini digunakan untuk mencari pelanggan berdasarkan data ONU, menampilkan status ONU, redaman optical power, informasi PPPoE, IP pelanggan, serta melakukan refresh data ONU per lokasi dan per PON.

---

## Fitur Utama

* Cari ONU berdasarkan nama pelanggan
* Menampilkan informasi pelanggan lengkap
* Menampilkan lokasi OLT
* Menampilkan data ONU, PON, ID, dan deskripsi
* Menampilkan status ONU online/offline
* Menampilkan redaman atau optical power
* Menampilkan informasi PPPoE dari MikroTik
* Refresh cache ONU per lokasi dan per PON
* Multi lokasi OLT
* Pembatasan akses user Telegram
* Hak akses khusus untuk refresh data
* Dapat berjalan otomatis menggunakan systemd

---

## Teknologi

Project ini menggunakan:

* Python
* python-telegram-bot
* RouterOS API
* SSH ke OLT ZTE C320
* JSON cache
* systemd service

---

## Struktur Folder

```text
olt-bot/
├── bot.py
├── handlers/
│   ├── start.py
│   ├── menu.py
│   ├── onu.py
│   ├── info.py
│   ├── refresh_onu.py
│   └── ...
├── services/
│   ├── ssh_client.py
│   ├── onu.py
│   ├── onu_cache.py
│   └── mikrotik.py
├── parser/
│   ├── detail_parser.py
│   ├── power_parser.py
│   └── ...
├── utils/
│   └── security.py
├── config/
│   ├── device.example.py
│   └── device.py
├── data/
│   ├── allowed_users.json
│   └── onu_cache.json
├── requirements.txt
└── README.md
```

---

## File Rahasia

File berikut tidak disarankan untuk diupload ke GitHub:

```text
.env
config/device.py
data/allowed_users.json
data/onu_cache.json
venv/
__pycache__/
*.pyc
```

Pastikan file tersebut sudah masuk ke `.gitignore`.

Contoh `.gitignore`:

```gitignore
.env
venv/
__pycache__/
*.pyc

config/device.py
data/allowed_users.json
data/onu_cache.json

*.log
```

---

## Contoh Konfigurasi Device

Gunakan file `config/device.example.py` sebagai contoh konfigurasi.

```python
DEVICES = {
    "LOKASI": {
        "olt": {
            "host": "IP_OLT",
            "port": 22,
            "username": "USER_OLT",
            "password": "PASSWORD_OLT",
            "ports": [
                "1/1/1",
                "1/1/2",
                "1/1/3",
                "1/1/4"
            ]
        },
        "mikrotik": {
            "host": "IP_MIKROTIK",
            "username": "USER_API",
            "password": "PASSWORD_API",
            "port": 8728
        }
    }
}
```

Jika OLT diakses melalui IP publik dengan port forwarding, gunakan port publik pada bagian `olt.port`.

Contoh:

```python
"olt": {
    "host": "103.xxx.xxx.xxx",
    "port": 5050,
    "username": "USER_OLT",
    "password": "PASSWORD_OLT"
}
```

---

## Contoh File Akses User

File akses user berada di:

```text
data/allowed_users.json
```

Contoh:

```json
{
    "owner_id": 123456789,
    "allowed_users": [
        123456789,
        987654321
    ],
    "refresh_admins": [
        123456789
    ]
}
```

Keterangan:

* `owner_id`: pemilik utama bot
* `allowed_users`: user yang boleh menggunakan bot
* `refresh_admins`: user yang boleh menjalankan refresh data ONU

---

## Instalasi

Masuk ke folder project:

```bash
cd /home/ggs/olt-bot
```

Buat virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependency:

```bash
pip install -r requirements.txt
```

Buat file `.env`:

```bash
nano .env
```

Isi token bot Telegram:

```env
BOT_TOKEN=ISI_TOKEN_BOT_TELEGRAM
```

---

## Menjalankan Bot Manual

```bash
cd /home/ggs/olt-bot
source venv/bin/activate
python3 bot.py
```

Jika berhasil, akan muncul:

```text
Bot running...
```

---

## Menjalankan Bot dengan Systemd

Contoh file service:

```ini
[Unit]
Description=OLT Monitoring Telegram Bot
After=network.target

[Service]
User=ggs
WorkingDirectory=/home/ggs/olt-bot
ExecStart=/home/ggs/olt-bot/venv/bin/python3 /home/ggs/olt-bot/bot.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Simpan sebagai:

```bash
/etc/systemd/system/oltbot.service
```

Aktifkan service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable oltbot
sudo systemctl start oltbot
```

Cek status:

```bash
sudo systemctl status oltbot
```

Lihat log realtime:

```bash
sudo journalctl -u oltbot -f
```

Restart bot:

```bash
sudo systemctl restart oltbot
```

---

## Command Telegram

Command utama:

```text
/start
/onu nama_pelanggan
/info nama_pelanggan
/myid
```

Command admin:

```text
/refresh_onu LOKASI PON
```

Contoh:

```text
/refresh_onu BALEN 1/1/1
/refresh_onu MAYANGKAWIS 1/1/1
/refresh_onu BALEN2 1/1/1
```

---

## Cara Kerja Bot

Alur sederhana:

```text
Telegram Bot
   |
   |-- SSH ke OLT ZTE C320
   |     |-- Ambil data ONU
   |     |-- Ambil detail status ONU
   |     |-- Ambil optical power
   |
   |-- API ke MikroTik
   |     |-- Ambil data PPPoE aktif
   |     |-- Ambil IP pelanggan
   |     |-- Ambil uptime PPPoE
   |
   |-- Simpan cache ONU ke data/onu_cache.json
```

---

## Refresh Data ONU

Refresh dilakukan untuk mengambil data konfigurasi ONU dari OLT dan menyimpannya ke cache.

Contoh:

```text
/refresh_onu BALEN 1/1/1
```

Setelah refresh berhasil, data akan tersimpan di:

```text
data/onu_cache.json
```

Data cache digunakan agar pencarian pelanggan lebih cepat.

---

## Catatan Penting

* Pastikan SSH OLT bisa diakses dari server bot
* Pastikan API MikroTik aktif
* Pastikan port OLT dan MikroTik sesuai konfigurasi
* Jika menggunakan IP publik, pastikan NAT dan firewall sudah benar
* Jangan upload token, password, IP sensitif, dan cache pelanggan ke GitHub
* Jika mengubah file `.py` atau `config/device.py`, restart service bot
* Jika hanya mengubah `allowed_users.json`, tidak perlu restart bot

---

## Git Workflow

Setelah ada perubahan kode:

```bash
git status
git add .
git commit -m "Update bot"
git push
```

Pastikan file sensitif tidak ikut masuk commit.

---

## Status Project

Project ini digunakan untuk monitoring OLT dan pelanggan PPPoE melalui Telegram Bot dengan integrasi OLT ZTE C320 dan MikroTik RouterOS API.
