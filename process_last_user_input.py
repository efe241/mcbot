import os
import sys
import json

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from database import db

TRANSCRIPT_PATH = r"C:\Users\EFE\.gemini\antigravity-cli\brain\f7599a6b-3bb6-48ad-b5d8-27ec03cd4603\.system_generated\logs\transcript_full.jsonl"

def process_last_prompt():
    if not os.path.exists(TRANSCRIPT_PATH):
        print(f"❌ Transcript bulunamadı: {TRANSCRIPT_PATH}")
        return

    user_text = ""
    with open(TRANSCRIPT_PATH, "r", encoding="utf-8") as f:
        for line in f:
            try:
                data = json.loads(line)
                if data.get("type") == "USER_INPUT":
                    content = data.get("content", "")
                    if "@hotmail" in content or "@outlook" in content or "@live" in content:
                        user_text = content
            except Exception:
                pass

    if not user_text:
        print("❌ Kullanıcı mesajı bulunamadı.")
        return

    # Extract lines
    lines = [line.strip() for line in user_text.splitlines() if line and line.strip() and ("@" in line)]
    print(f"📦 Ayıklanan Toplam Hesap Sayısı: {len(lines)} adet.")

    added_count = db.add_stock("hotmail_free", lines)
    total_stock = db.get_stock_count("hotmail_free")

    print(f"✅ Hotmail stoklarına {added_count} adet hesap başarıyla eklendi!")
    print(f"📊 Güncel Toplam Hotmail Stoğu: {total_stock} adet")

if __name__ == "__main__":
    process_last_prompt()
