import os
import sys
import json

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from database import db, STOCKS_FILE, _lock, _read_json, _write_json

def transfer_stock():
    with _lock:
        stocks = _read_json(STOCKS_FILE, {})
        free_accs = stocks.get("hotmail_free", [])
        total_free = len(free_accs)
        
        print(f"📦 Mevcut Hotmail Free Stok: {total_free} adet")
        
        if total_free <= 20:
            print("⚠️ Free stokta zaten 20 veya daha az hesap var, aktarma yapılmadı.")
            return

        keep_free = free_accs[:20]
        move_to_vip = free_accs[20:]

        stocks["hotmail_free"] = keep_free
        
        if "hotmail_vip" not in stocks:
            stocks["hotmail_vip"] = []
            
        stocks["hotmail_vip"].extend(move_to_vip)

        _write_json(STOCKS_FILE, stocks)

        print(f"✅ İşlem Başarılı!")
        print(f"• Hotmail Free Kalan Stok: {len(stocks['hotmail_free'])} adet")
        print(f"• Hotmail VIP Yeni Stok: {len(stocks['hotmail_vip'])} adet ({len(move_to_vip)} adet aktarıldı)")

if __name__ == "__main__":
    transfer_stock()
