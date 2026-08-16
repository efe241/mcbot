import json
import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

DATA_DIR = r"C:\Users\EFE\Desktop\mcbot\data"
STOCKS_FILE = os.path.join(DATA_DIR, "stocks.json")

raw_codes = [
    "TBAAj8YjaGDA",
    "TBAAPs4J8u4u",
    "TBAAYzs78cfH",
    "TBAAyScH7Qzy",
    "TBAAz3HHUNm9",
    "TBAA5qjkzPUU",
    "TBAA7DkWf9XH",
    "TBAADmtuA9H7",
    "TBAAkq2ddZgG",
    "TBAAjZgpj8qN",
    "TBAAdxSmpnDz",
    "TBAAPXuNDG5J",
    "TBAAQMfDNhzb",
    "TBAAWeLvjWMu",
    "TBAAw2je9njA"
]

formatted_items = [
    f"Kod: {code} | Kullanım Linki: https://www.exxen.com/tr/promosyon-kodu | SKT: 31.12.2026"
    for code in raw_codes
]

free_codes = formatted_items[:5]
vip_codes = formatted_items[5:]

if os.path.exists(STOCKS_FILE):
    with open(STOCKS_FILE, "r", encoding="utf-8") as f:
        stocks = json.load(f)

    stocks["exxen_free"] = free_codes
    stocks["exxen_vip"] = vip_codes

    with open(STOCKS_FILE, "w", encoding="utf-8") as f:
        json.dump(stocks, f, ensure_ascii=False, indent=2)

    print(f"OK: exxen_free stoğuna {len(free_codes)} adet eklendi.")
    print(f"OK: exxen_vip stoğuna {len(vip_codes)} adet eklendi.")
