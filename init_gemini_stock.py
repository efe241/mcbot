import json
import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

stocks_file = r"C:\Users\EFE\Desktop\mcbot\data\stocks.json"

if os.path.exists(stocks_file):
    try:
        with open(stocks_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        data["gemini_pro"] = ["efe674841@gmail.com:Me261211@"]
        with open(stocks_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("OK: gemini_pro stoklari eklendi.")
    except Exception as e:
        print(f"Hata: {e}")
