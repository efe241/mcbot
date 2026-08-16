import json
import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

DATA_DIR = r"C:\Users\EFE\Desktop\mcbot\data"
SERVICES_FILE = os.path.join(DATA_DIR, "services.json")
STOCKS_FILE = os.path.join(DATA_DIR, "stocks.json")

tod_acc = "emirhankorkut@yahoo.com.tr:2003Emirhan"

# Update services.json
if os.path.exists(SERVICES_FILE):
    try:
        with open(SERVICES_FILE, "r", encoding="utf-8") as f:
            services = json.load(f)
        
        for s in services:
            if s.get("id") == "tod_tv_free":
                s["is_unlimited"] = False
                s["name"] = "TOD TV Free"
                s["description"] = "Ücretsiz TOD TV Hesap Servisi (5 Adet Sınırlı Stok)"
            elif s.get("id") == "tod_tv_vip":
                s["is_unlimited"] = True
                s["name"] = "TOD TV Premium VIP 4K (Sınırsız)"
                s["description"] = "VIP Özel TOD TV Dizi/Film/Spor Üyeliği (Sınırsız)"

        with open(SERVICES_FILE, "w", encoding="utf-8") as f:
            json.dump(services, f, ensure_ascii=False, indent=2)
        print("OK: services.json güncellendi (tod_tv_free limitsiz yapıldı, tod_tv_vip sınırsız)")
    except Exception as e:
        print(f"Hata services.json: {e}")

# Update stocks.json
if os.path.exists(STOCKS_FILE):
    try:
        with open(STOCKS_FILE, "r", encoding="utf-8") as f:
            stocks = json.load(f)
        
        stocks["tod_tv_free"] = [tod_acc] * 5
        stocks["tod_tv_vip"] = [tod_acc]

        with open(STOCKS_FILE, "w", encoding="utf-8") as f:
            json.dump(stocks, f, ensure_ascii=False, indent=2)
        print("OK: stocks.json güncellendi (tod_tv_free 5 stok, tod_tv_vip 1 sınırsız stok)")
    except Exception as e:
        print(f"Hata stocks.json: {e}")
