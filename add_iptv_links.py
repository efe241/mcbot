import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from database import db

iptv_links = [
    "📺 IPTV Stream M3U8: http://92.113.151.217/test3/index.m3u8",
    "🌐 IPTV Web Embed Player: http://92.113.151.217/test3/embed.html"
]

added_count = db.add_stock("iptv_free", iptv_links)
total_stock = db.get_stock_count("iptv_free")

print(f"✅ {added_count} adet IPTV linki 'iptv_free' stoklarına eklendi!")
print(f"📊 Güncel IPTV Free Stoğu: {total_stock} adet")
