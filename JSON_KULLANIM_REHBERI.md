# 📄 JSON Dosyaları İle Servis ve Stok Düzenleme Rehberi

Artık Not Defteri (Notepad) veya herhangi bir metin editörü ile `data` klasöründeki JSON dosyalarını açıp dilediğiniz gibi yeni servisler ekleyebilir veya stok yükleyebilirsiniz!

---

## 📂 1. Servis/Kategori Ekleme (`data/services.json`)

`C:\Users\EFE\Desktop\mcbot\data\services.json` dosyasını Not Defteri ile açın.

Yeni bir servis eklemek için en alta şu şekilde yeni bir blok ekleyin:

```json
[
  {
    "id": "blutv_free",
    "name": "BluTV Ücretsiz",
    "category": "free",
    "emoji": "📺",
    "description": "Ücretsiz BluTV Hesapları"
  },
  {
    "id": "exxen_vip",
    "name": "Exxen Spor VIP",
    "category": "vip",
    "emoji": "⚽",
    "description": "VIP Özel Exxen Spor Paket Hesapları"
  }
]
```

### 📌 Alanların Anlamları:
- **`id`**: Servisin benzersiz kod adıdır. Küçük harfle yazılmalı ve boşluk yerine alt çizgi `_` kullanılmalıdır (Örn: `blutv_free`).
- **`name`**: Discord menüsünde kullanıcıların göreceği isim (Örn: `BluTV Ücretsiz`).
- **`category`**: Servisin kategorisidir.
  - **`"free"`**: Herkesin alabileceği ücretsiz servis.
  - **`"vip"`**: Sadece VIP üyelerin alabileceği özel servis.
- **`emoji`**: Servis isminin yanındaki emoji (Örn: `📺`, `🎮`, `👑`).
- **`description`**: Kısa açıklama.

---

## 📦 2. Manuel Stok Yükleme (`data/stocks.json`)

`C:\Users\EFE\Desktop\mcbot\data\stocks.json` dosyasını Not Defteri ile açın.

İlgili servisin `id` isminin yanına hesaplarınızı tırnak içinde virgülle ayırarak yapıştırın:

```json
{
  "netflix_free": [
    "hesap1@gmail.com:sifre123",
    "hesap2@gmail.com:sifre456",
    "hesap3@gmail.com:sifre789"
  ],
  "blutv_free": [
    "blutv_user@gmail.com:pass123"
  ]
}
```

> ⚠️ **İpucu:** Ayrıca bot çalışırken Discord üzerinden **`/stok-ekle`** veya **`🛠️ Admin Paneli`** butonuna basarak da stok yükleyebilirsiniz. Bot ikisini de otomatik eşitler!
