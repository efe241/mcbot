import os
import sys
import json
from database import db

def load_from_txt(service_id, txt_filepath):
    if not os.path.exists(txt_filepath):
        print(f"❌ HATA: '{txt_filepath}' dosyası bulunamadı!")
        return

    service = db.get_service(service_id)
    if not service:
        services = db.get_services()
        ids = ", ".join([s["id"] for s in services])
        print(f"❌ HATA: '{service_id}' adlı servis bulunamadı!\nMevcut Servisler: {ids}")
        return

    print(f"⏳ '{txt_filepath}' okunuyor...")
    with open(txt_filepath, "r", encoding="utf-8", errors="ignore") as f:
        lines = [line.strip() for line in f if line.strip()]

    print(f"📦 Bulunan toplam satır sayısı: {len(lines)} adet.")
    added_count = db.add_stock(service_id, lines)
    total = db.get_stock_count(service_id)

    print(f"✅ BAŞARILI! '{service['name']}' servisine {added_count} adet stok eklendi.")
    print(f"📊 Toplam Güncel Stok: {total} adet")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("====================================================")
        print("📌 TOPLU STOK YÜKLEYİCİ (10.000+ HESAP DESTEĞİ)")
        print("====================================================")
        print("Kullanım Şekli:")
        print("  python stok_yukle.py <servis_id> <dosya_yolu.txt>")
        print("\nÖrnek:")
        print("  python stok_yukle.py hotmail_free eldeki_hesaplar.txt")
        print("====================================================")
    else:
        s_id = sys.argv[1]
        f_path = sys.argv[2]
        load_from_txt(s_id, f_path)
