# 🤖 Discord Generator & Stok Botu (Python)

Bu bot; Discord sunucunuzda **Free (Ücretsiz)** ve **VIP (Ayrıcalıklı)** kullanıcılar için otomatik hesap/kod dağıtımı (Generator) yapmanızı sağlayan gelişmiş ve modern bir Discord botudur.

---

## 🌟 Özellikler

- 🎁 **FREE & ⭐ VIP Butonlu Panel**: Kullanıcılar butonlara tıklayarak doğrudan istedikleri servisi seçebilir.
- 📩 **DM (Özel Mesaj) Teslimatı**: Stoktan çekilen hesaplar kullanıcıya özel mesajla iletilir. DM kapalıysa güvenli geçici mesaj gösterilir.
- ⏱️ **Günlük Hak & Cooldown Sistemi**:
  - **Free Üyeler:** Günlük 1 stok hakkı (24 saatte bir yenilenir).
  - **VIP Üyeler:** Günlük daha fazla hak (Örn: 5 stok hakkı) veya özel stoklar.
  - Canlı geri sayım sayacı (`3 saat 12 dakika kaldı` gibi).
- 📦 **Gelişmiş Stok Yönetimi**:
  - `/stok-ekle`: Discord içerisinde açılan **Modal (Pop-up Form Window)** üzerinden toplu olarak yüzlerce hesabı tek tıkla yapıştırıp ekleyin.
  - `/stok-temizle`: İstenen servisin stoğunu sıfırlama.
  - `/stok-liste`: Tüm servislerin anlık stok durumunu detaylı inceleme.
  - `/servis-ekle` / `/servis-sil`: Canlı olarak yeni servisler (Örn: Disney+, Minecraft Mail, Netflix, Spotify) tanımlama.
- 📜 **Log Kanalı Entegrasyonu**: Her stok teslimatı yetkili log kanalına otomatik bildirim atar.
- 🔄 **Kalıcı Butonlar (Persistent Views)**: Bot yeniden başlasa bile butonlar bozulmaz, çalışmaya devam eder.

---

## 🚀 Kurulum Adımları

### 1. Discord Bot Tokenini Alma ve İzinleri Ayarlama
1. [Discord Developer Portal](https://discord.com/developers/applications) adresine gidin.
2. **New Application** butonuna basarak bir uygulama oluşturun.
3. Sol menüden **Bot** sekmesine gidin.
4. **Reset Token** butonuna basarak tokeninizi kopyalayın.
5. **Privileged Gateway Intents** altındaki şu iki seçeneği **AÇIK (ON)** duruma getirin:
   - ✅ **Server Members Intent**
   - ✅ **Message Content Intent**
6. **OAuth2 -> URL Generator** sekmesine gidin:
   - `bot` ve `applications.commands` kutularını işaretleyin.
   - İzinlerden `Administrator` (veya Mesaj Gönder, Embed Bağlantıları, vb.) seçip üretilen davet linki ile botu sunucunuza ekleyin.

---

### 2. Konfigürasyon (`.env`)
Klasördeki `.env` dosyasını Not Defteri veya bir kod editörü ile açıp bilgilerinizi girin:

```env
DISCORD_TOKEN=MTE... (Kopyaladığınız Bot Tokeni)
GUILD_ID=123456789012345678 (Sunucu ID'niz - Anında komut senkronizasyonu için)
LOG_CHANNEL_ID=123456789012345678 (Stok log kanalının ID'si)
```

---

### 3. Botu Çalıştırma

#### Windows Üzerinde (Tek Tıkla):
Klasördeki **`baslat.bat`** dosyasına çift tıklamanız yeterlidir. Gerekli kütüphaneleri otomatik yükleyip botu başlatacaktır.

#### Terminal / Komut Satırından:
```bash
python -m pip install -r requirements.txt
python main.py
```

---

## 🛠️ Yönetici Komutları

Bot çalıştıktan sonra sunucunuzda aşağıdaki **Slash (/)** komutlarını kullanabilirsiniz:

| Komut | Açıklama |
| :--- | :--- |
| `/panel` | Ana Free/VIP butonlu mesaj panelini belirtilen kanala kurar. |
| `/stok-ekle [servis_id]` | Açılan pencerede hesapları satır satır yapıştırıp stok yüklersiniz. |
| `/stok-liste` | Tüm servislerin güncel stok durumunu listeler. |
| `/stok-temizle [servis_id]` | İlgili servisin tüm stoklarını siler. |
| `/servis-ekle` | Yeni bir servis tanımlar (Örn: Steam Key, Disney+ vb.). |
| `/servis-sil` | Bir servisi tamamen sistemden kaldırır. |
| `/hak-sifirla [kullanici]` | Bir kullanıcının günlük bekleme süresini sıfırlar. |
| `/ayarlar` | Cooldown süresi, VIP rolü ve günlük hak limitlerini değiştirir. |

---

## 📁 Dosya Yapısı

```
mcbot/
├── .env                  # Bot token ve sunucu ayarları
├── .env.example          # Şablon env dosyası
├── requirements.txt      # Gerekli Python kütüphaneleri
├── baslat.bat            # Windows başlatıcı
├── database.py           # JSON Veritabanı ve Cooldown Mantığı
├── main.py               # Bot ana koda yapısı ve UI Elemanları
└── data/                 # Stok ve kullanıcı verilerinin tutulduğu klasör
    ├── config.json
    ├── services.json
    ├── stocks.json
    └── users.json
```
