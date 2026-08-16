import json
import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

DATA_DIR = r"C:\Users\EFE\Desktop\mcbot\data"
SERVICES_FILE = os.path.join(DATA_DIR, "services.json")
STOCKS_FILE = os.path.join(DATA_DIR, "stocks.json")

# Update services.json to mark mc_vip as is_unlimited: True
if os.path.exists(SERVICES_FILE):
    try:
        with open(SERVICES_FILE, "r", encoding="utf-8") as f:
            services = json.load(f)
        for s in services:
            if s.get("id") == "mc_vip":
                s["is_unlimited"] = True
                s["name"] = "Minecraft Premium Full Access"
        with open(SERVICES_FILE, "w", encoding="utf-8") as f:
            json.dump(services, f, ensure_ascii=False, indent=2)
        print("OK: services.json güncellendi (mc_vip is_unlimited=True)")
    except Exception as e:
        print(f"Hata services.json: {e}")

# Update stocks.json to set mc_vip stock to ["retosatis35@outlook.com:Reto2001@"]
if os.path.exists(STOCKS_FILE):
    try:
        with open(STOCKS_FILE, "r", encoding="utf-8") as f:
            stocks = json.load(f)
        stocks["mc_vip"] = ["retosatis35@outlook.com:Reto2001@"]
        with open(STOCKS_FILE, "w", encoding="utf-8") as f:
            json.dump(stocks, f, ensure_ascii=False, indent=2)
        print("OK: stocks.json güncellendi (mc_vip stoğu eklendi)")
    except Exception as e:
        print(f"Hata stocks.json: {e}")
