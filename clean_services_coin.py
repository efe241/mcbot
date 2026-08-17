import json
import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

DATA_DIR = r"C:\Users\EFE\Desktop\mcbot\data"
SERVICES_FILE = os.path.join(DATA_DIR, "services.json")

if os.path.exists(SERVICES_FILE):
    with open(SERVICES_FILE, "r", encoding="utf-8") as f:
        services = json.load(f)

    for s in services:
        if s["id"] == "gemini_pro":
            s["name"] = "Google Gemini Pro (Sınırsız)"
            s["description"] = "VIP Özel Google Gemini Pro Hesap"
        elif s["id"] == "nitro_promo":
            s["name"] = "Discord Nitro Promo (Ticket)"
            s["description"] = "VIP Özel Discord Nitro Promo (Ticket Açılır)"
        elif s["id"] == "spotify_premium_vip":
            s["name"] = "Spotify Premium Bireysel (Ticket)"
            s["description"] = "VIP Özel Spotify Premium Bireysel (Ticket Açılır)"

    with open(SERVICES_FILE, "w", encoding="utf-8") as f:
        json.dump(services, f, ensure_ascii=False, indent=2)
    print("OK: services.json temizlendi (coin ibareleri kaldırıldı)")
