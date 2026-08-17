import json
import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

DATA_DIR = r"C:\Users\EFE\Desktop\mcbot\data"
SERVICES_FILE = os.path.join(DATA_DIR, "services.json")
STOCKS_FILE = os.path.join(DATA_DIR, "stocks.json")

sim_acc = "dimitris9027@hotmail.com:quattro9027"

# Update services.json
if os.path.exists(SERVICES_FILE):
    try:
        with open(SERVICES_FILE, "r", encoding="utf-8") as f:
            services = json.load(f)
        
        exists = False
        for s in services:
            if s.get("id") == "simmarket_vip":
                s["name"] = "SimMarket VIP (Sınırsız)"
                s["category"] = "vip"
                s["emoji"] = "✈️"
                s["description"] = "VIP Özel SimMarket Hesabı (Sınırsız)"
                s["is_unlimited"] = True
                exists = True
                break
        if not exists:
            services.append({
                "id": "simmarket_vip",
                "name": "SimMarket VIP (Sınırsız)",
                "category": "vip",
                "emoji": "✈️",
                "description": "VIP Özel SimMarket Hesabı (Sınırsız)",
                "is_unlimited": True
            })

        with open(SERVICES_FILE, "w", encoding="utf-8") as f:
            json.dump(services, f, ensure_ascii=False, indent=2)
        print("OK: services.json güncellendi (simmarket_vip eklendi)")
    except Exception as e:
        print(f"Hata services.json: {e}")

# Update stocks.json
if os.path.exists(STOCKS_FILE):
    try:
        with open(STOCKS_FILE, "r", encoding="utf-8") as f:
            stocks = json.load(f)
        
        stocks["simmarket_vip"] = [sim_acc]

        with open(STOCKS_FILE, "w", encoding="utf-8") as f:
            json.dump(stocks, f, ensure_ascii=False, indent=2)
        print("OK: stocks.json güncellendi (simmarket_vip eklendi)")
    except Exception as e:
        print(f"Hata stocks.json: {e}")
