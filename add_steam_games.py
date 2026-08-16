import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from database import db

steam_items = [
    "🎮 SuperMarket Simulator | K.Adı: afta53298 | Şifre: AndreiPadure199",
    "🎮 Assetto Corsa | K.Adı: wbtq1085833 | Şifre: steamok222111",
    "🎮 Internet Cafe Simulator 2 | K.Adı: 947214940 | Şifre: NPlHvJQViI",
    "🎮 Car For Sale Simulator | K.Adı: rftlw79673 | Şifre: mqpt78216F",
    "🎮 GTA 5 | K.Adı: berk1158 | Şifre: arifkaya2007",
    "🎮 Marvel's Spider-Man | K.Adı: cnykqx48s | Şifre: Progamer@",
    "🎮 Forza Horizon 5 | K.Adı: ya3Ij0Dv5Jy5 | Şifre: Cano#2002",
    "🎮 Euro Truck Simulator 2 | K.Adı: dionildo3 | Şifre: Dhodho23",
    "🎮 BeamNG.drive | K.Adı: egbdb28825 | Şifre: qpwoei12345@"
]

added_count = db.add_stock("steam_free", steam_items)
total_stock = db.get_stock_count("steam_free")

print(f"✅ {added_count} adet oyunlu Steam hesabı 'steam_free' stoklarına eklendi!")
print(f"📊 Güncel Steam Stoğu: {total_stock} adet")
