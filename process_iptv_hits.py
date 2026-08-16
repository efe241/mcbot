import os
import sys
import json
import re

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from database import db

TRANSCRIPT_PATH = r"C:\Users\EFE\.gemini\antigravity-cli\brain\f7599a6b-3bb6-48ad-b5d8-27ec03cd4603\.system_generated\logs\transcript_full.jsonl"

def process_iptv_prompt():
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
                    if "redworld.pro" in content or "m3u" in content.lower():
                        user_text = content
            except Exception:
                pass

    if not user_text:
        print("❌ Kullanıcı IPTV mesajı bulunamadı.")
        return

    # Extract all M3U links or user:pass credentials
    m3u_links = re.findall(r'http://redworld\.pro:\d+/get\.php\?username=[^\s&]+&password=[^\s&]+[^\s]*', user_text)
    
    # Also fallback to user/pass extraction if m3u links not found
    if not m3u_links:
        users = re.findall(r'ᴜꜱᴇʀ\s*:\s*([^\s\n]+)', user_text)
        passes = re.findall(r'ᴩᴀꜱꜱ\s*:\s*([^\s\n]+)', user_text)
        m3u_links = [f"🌐 IPTV | User: {u} | Pass: {p} | Host: http://redworld.pro:8880" for u, p in zip(users, passes)]

    # Deduplicate while preserving order
    unique_links = list(dict.fromkeys(m3u_links))

    print(f"📦 Toplam Ayıklanan Benzersiz IPTV Hesabı/Linki: {len(unique_links)} adet.")

    added_count = db.add_stock("iptv_vip", unique_links)
    total_stock = db.get_stock_count("iptv_vip")

    print(f"✅ IPTV VIP stoklarına {added_count} adet hesap/link başarıyla eklendi!")
    print(f"📊 Güncel Toplam IPTV VIP Stoğu: {total_stock} adet")

if __name__ == "__main__":
    process_iptv_prompt()
