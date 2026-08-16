import json
import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

DATA_DIR = r"C:\Users\EFE\Desktop\mcbot\data"
SERVICES_FILE = os.path.join(DATA_DIR, "services.json")
STOCKS_FILE = os.path.join(DATA_DIR, "stocks.json")

tod_acc = "emirhankorkut@yahoo.com.tr:2003Emirhan"

# Update services.json to add tod_tv_free and tod_tv_vip
if os.path.exists(SERVICES_FILE):
    try:
        with open(SERVICES_FILE, "r", encoding="utf-8") as f:
            services = json.load(f)
        
        existing_ids = [s.get("id") for s in services]
        
        if "tod_tv_free" not in existing_ids:
            services.append({
                "id": "tod_tv_free",
                "name": "TOD TV Free",
                "category": "free",
                "emoji": "📺",
                "description": "Ücretsiz TOD TV Hesap Servisi",
                "is_unlimited": True
            })
        if "tod_tv_vip" not in existing_ids:
            services.append({
                "id": "tod_tv_vip",
                "name": "TOD TV Premium VIP 4K",
                "category": "vip",
                "emoji": "📺",
                "description": "VIP Özel TOD TV Dizi/Film/Spor Üyeliği",
                "is_unlimited": True
            })

        with open(SERVICES_FILE, "w", encoding="utf-8") as f:
            json.dump(services, f, ensure_ascii=False, indent=2)
        print("OK: services.json güncellendi (tod_tv eklendi)")
    except Exception as e:
        print(f"Hata services.json: {e}")

# Update stocks.json to set tod_tv stock to ["emirhankorkut@yahoo.com.tr:2003Emirhan"]
if os.path.exists(STOCKS_FILE):
    try:
        with open(STOCKS_FILE, "r", encoding="utf-8") as f:
            stocks = json.load(f)
        stocks["tod_tv_free"] = [tod_acc]
        stocks["tod_tv_vip"] = [tod_acc]
        with open(STOCKS_FILE, "w", encoding="utf-8") as f:
            json.dump(stocks, f, ensure_ascii=False, indent=2)
        print("OK: stocks.json güncellendi (tod_tv stoğu eklendi)")
    except Exception as e:
        print(f"Hata stocks.json: {e}")
