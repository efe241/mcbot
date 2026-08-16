import json
import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

DATA_DIR = r"C:\Users\EFE\Desktop\mcbot\data"
SERVICES_FILE = os.path.join(DATA_DIR, "services.json")
STOCKS_FILE = os.path.join(DATA_DIR, "stocks.json")

# Update services.json to add tonguc_vip as is_unlimited: True
if os.path.exists(SERVICES_FILE):
    try:
        with open(SERVICES_FILE, "r", encoding="utf-8") as f:
            services = json.load(f)
        
        # Check if tonguc_vip exists
        exists = False
        for s in services:
            if s.get("id") == "tonguc_vip":
                s["name"] = "Tonguç Akademi VIP (Sınırsız)"
                s["category"] = "vip"
                s["emoji"] = "📚"
                s["description"] = "VIP Özel Tonguç Akademi Hesap (Sınırsız)"
                s["is_unlimited"] = True
                exists = True
                break
        if not exists:
            services.append({
                "id": "tonguc_vip",
                "name": "Tonguç Akademi VIP (Sınırsız)",
                "category": "vip",
                "emoji": "📚",
                "description": "VIP Özel Tonguç Akademi Hesap (Sınırsız)",
                "is_unlimited": True
            })

        with open(SERVICES_FILE, "w", encoding="utf-8") as f:
            json.dump(services, f, ensure_ascii=False, indent=2)
        print("OK: services.json güncellendi (tonguc_vip eklendi)")
    except Exception as e:
        print(f"Hata services.json: {e}")

# Update stocks.json to set tonguc_vip stock to ["arslandevrim2@gmail.com:gmailfail098"]
if os.path.exists(STOCKS_FILE):
    try:
        with open(STOCKS_FILE, "r", encoding="utf-8") as f:
            stocks = json.load(f)
        stocks["tonguc_vip"] = ["arslandevrim2@gmail.com:gmailfail098"]
        with open(STOCKS_FILE, "w", encoding="utf-8") as f:
            json.dump(stocks, f, ensure_ascii=False, indent=2)
        print("OK: stocks.json güncellendi (tonguc_vip stoğu eklendi)")
    except Exception as e:
        print(f"Hata stocks.json: {e}")
