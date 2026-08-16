import json
import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

DATA_DIR = r"C:\Users\EFE\Desktop\mcbot\data"
SERVICES_FILE = os.path.join(DATA_DIR, "services.json")
STOCKS_FILE = os.path.join(DATA_DIR, "stocks.json")

smm_acc = "https://cheapestsmmpanels.com:Anonhax:20112008@"

# Update services.json
if os.path.exists(SERVICES_FILE):
    try:
        with open(SERVICES_FILE, "r", encoding="utf-8") as f:
            services = json.load(f)
        
        exists = False
        for s in services:
            if s.get("id") == "smm_vip":
                s["name"] = "Cheapest SMM Panels VIP"
                s["category"] = "vip"
                s["emoji"] = "🔑"
                s["description"] = "VIP Özel CheapestSMMPanels Hesabı"
                s["is_unlimited"] = False
                exists = True
                break
        if not exists:
            services.append({
                "id": "smm_vip",
                "name": "Cheapest SMM Panels VIP",
                "category": "vip",
                "emoji": "🔑",
                "description": "VIP Özel CheapestSMMPanels Hesabı",
                "is_unlimited": False
            })

        with open(SERVICES_FILE, "w", encoding="utf-8") as f:
            json.dump(services, f, ensure_ascii=False, indent=2)
        print("OK: services.json güncellendi (smm_vip eklendi)")
    except Exception as e:
        print(f"Hata services.json: {e}")

# Update stocks.json
if os.path.exists(STOCKS_FILE):
    try:
        with open(STOCKS_FILE, "r", encoding="utf-8") as f:
            stocks = json.load(f)
        
        stocks["smm_vip"] = [smm_acc] * 10

        with open(STOCKS_FILE, "w", encoding="utf-8") as f:
            json.dump(stocks, f, ensure_ascii=False, indent=2)
        print("OK: stocks.json güncellendi (smm_vip 10 stok eklendi)")
    except Exception as e:
        print(f"Hata stocks.json: {e}")
