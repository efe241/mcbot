import json
import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

DATA_DIR = r"C:\Users\EFE\Desktop\mcbot\data"
CONFIG_FILE = os.path.join(DATA_DIR, "config.json")

channel_id = "1538560333545738281"

if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    
    cfg["announcement_channel_id"] = channel_id

    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)
    print(f"OK: config.json güncellendi (announcement_channel_id: {channel_id})")
