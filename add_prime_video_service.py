import json
import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

DATA_DIR = r"C:\Users\EFE\Desktop\mcbot\data"
SERVICES_FILE = os.path.join(DATA_DIR, "services.json")
STOCKS_FILE = os.path.join(DATA_DIR, "stocks.json")

prime_cookie_text = """# Netscape HTTP Cookie File
.primevideo.com\tTRUE\t/\tTRUE\t1790306055\tat-main-av\tAtza|IwEBIEPnKEh4SmQvmLNbb4ZmsYR1ns8w97fNd20fCtKHev846Qa5JPCdwctdBUZ0s6yK3JiX7vASaPke2MxcCedNmflGiFEUfq1C0UkoVm2s8LHHdAUafzqfQ1i7oz6rhrGxNiOwFYfcBUt6uHsZaoMC2z0v_xjTGHScaGrdT9v6lXavWfKeTZHhxzOZ033VEHR_Xz-mhxGXaaUPddvAJ2P9jLNFF_UfBDWh9X0-fzyWmypx_24haG8z4zUQFeR9TSzm8vI
.primevideo.com\tTRUE\t/\tFALSE\t1790306055\ti18n-prefs\tUSD
.primevideo.com\tTRUE\t/\tFALSE\t1790306055\tlc-main-av\ten_US
.primevideo.com\tTRUE\t/\tTRUE\t1790306055\tsess-at-main-av\t"yKtjrw6YOQWz84EkX42ku3yP8E5FXLxcNbSJo8K7Enc="
.primevideo.com\tTRUE\t/\tTRUE\t1790306055\tsession-id-time\t2082787201l
.primevideo.com\tTRUE\t/\tTRUE\t1790306055\tsession-token\tqJ2dHmohOI+egqxQzJo9oHwGfJS1Md/WRO2L+nsHRsNKfZ2E9Ebalu8cIEtSymmDFtYVJYYKMNqDw31aurrd/oDHR5DbbXavZIMtDhzfahe9eyWHZLKr7bQ759/LNw3YTyuamFGquOHcubxtL+8wI8D97e5t9xBURl+9Cd4SPqN2cvUfaDXNX+0GMXbNh6/M6O/1t1RN38WNm4MBjPZ0NYHMWiy3Q/hI0fi80kSUPp6l+JxhC7zdSwlMgV4mg6n5ebBUkx+L/JD9jBBwYMENQDTriMDbBo4Kxk4ugpsz/jzcZAMM7U3ldADhZgzdY7XhoCGTy7ZUdcXR0BELDZW5TkIGdfkgYtyZlz3ARWSU23J2p1YM08GICVDXExPHVmIx
.primevideo.com\tTRUE\t/\tTRUE\t1790306055\tubid-main-av\t260-9405880-5673007
.primevideo.com\tTRUE\t/\tTRUE\t1790306055\tx-main-av\t"IJm8u1LjM7OWEw9FwslJLE9NX7l2CMwXbfgmgX9@KEmy?eKGcsvQxxuNFhlgfZty"
www.primevideo.com\tFALSE\t/\tFALSE\t1789010087\tcsm-hit\ttb:PWT0V8097V6V6WGR46MJ+s-J6AS6PR3KZ5CWA1BQ7CG|1758770087089&t:1758770087089&adb:adblk_no
.primevideo.com\tTRUE\t/\tTRUE\t1793330348\tsession-id\t261-0943717-0251564
.primevideo.com\tTRUE\t/\tFALSE\t1790306532\tav-timezone\tAsia/Calcutta"""

# Update services.json
if os.path.exists(SERVICES_FILE):
    try:
        with open(SERVICES_FILE, "r", encoding="utf-8") as f:
            services = json.load(f)
        
        exists = False
        for s in services:
            if s.get("id") == "prime_video_vip":
                s["name"] = "Amazon Prime Video Cookie (Sınırsız)"
                s["category"] = "vip"
                s["emoji"] = "🎬"
                s["description"] = "VIP Özel Prime Video Cookie (Cookie Editor İle Giriş)"
                s["is_unlimited"] = True
                exists = True
                break
        if not exists:
            services.append({
                "id": "prime_video_vip",
                "name": "Amazon Prime Video Cookie (Sınırsız)",
                "category": "vip",
                "emoji": "🎬",
                "description": "VIP Özel Prime Video Cookie (Cookie Editor İle Giriş)",
                "is_unlimited": True
            })

        with open(SERVICES_FILE, "w", encoding="utf-8") as f:
            json.dump(services, f, ensure_ascii=False, indent=2)
        print("OK: services.json güncellendi (prime_video_vip eklendi)")
    except Exception as e:
        print(f"Hata services.json: {e}")

# Update stocks.json
if os.path.exists(STOCKS_FILE):
    try:
        with open(STOCKS_FILE, "r", encoding="utf-8") as f:
            stocks = json.load(f)
        
        stocks["prime_video_vip"] = [prime_cookie_text]

        with open(STOCKS_FILE, "w", encoding="utf-8") as f:
            json.dump(stocks, f, ensure_ascii=False, indent=2)
        print("OK: stocks.json güncellendi (prime_video_vip stoğu eklendi)")
    except Exception as e:
        print(f"Hata stocks.json: {e}")
