import os
import json
import time
import random
from datetime import datetime, timedelta
import threading

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

os.makedirs(DATA_DIR, exist_ok=True)

SERVICES_FILE = os.path.join(DATA_DIR, "services.json")
STOCKS_FILE = os.path.join(DATA_DIR, "stocks.json")
USERS_FILE = os.path.join(DATA_DIR, "users.json")
CONFIG_FILE = os.path.join(DATA_DIR, "config.json")
KEYS_FILE = os.path.join(DATA_DIR, "keys.json")
LOGS_FILE = os.path.join(DATA_DIR, "logs.json")

# Re-entrant Lock
_lock = threading.RLock()

DEFAULT_CONFIG = {
    "cooldown_hours": 24,
    "free_daily_limit": 1,
    "vip_daily_limit": 2,
    "booster_daily_limit": 3,
    "admin_role_id": 0,
    "vip_role_id": 0,
    "log_channel_id": 0,
    "announcement_channel_id": "1538560333545738281",
    "required_status": "LeaksTr",
    "min_account_age_days": 7,
    "invites_for_vip": 5
}

PRIME_COOKIE_TEXT = """# Netscape HTTP Cookie File
.primevideo.com\tTRUE\t/\tTRUE\t1790306055\tat-main-av\tAtza|IwEBIEPnKEh4SmQvmLNbb4ZmsYR1ns8w97fNd20fCtKHev846Qa5JPCdwctdBUZ0s6yK3JiX7vASaPke2MxcCedNmflGiFEUfq1C0UkoVm2s8LHHdAUafzqfQ1i7oz6rhrGxNiOwFYfcBUt6uHsZaoMC2z0v_xjTGHScaGrdT9v6lXavWfKeTZHhxzOZ033VEHR_Xz-mhxGXaaUPddvAJ2P9jLNFF_UfBDWh9X0-fzyWmypx_24haG8z4zUQFeR9TSzm8vI
.primevideo.com\tTRUE\t/\tFALSE\t1790306055\ti18n-prefs\tUSD
.primevideo.com\tTRUE\t/\tFALSE\t1790306055\tlc-main-av\ten_US
.primevideo.com\tTRUE\t/\tTRUE\t1790306055\tsess-at-main-av\t"yKtjrw6YOQWz84EkX42ku3yP8E5FXLxcNbSJo8K7Enc="
.primevideo.com\tTRUE\t/\tTRUE\t1790306055\tsession-id-time\t2082787201l
.primevideo.com\tTRUE\t/\tTRUE\t1790306055\tsession-token\tqJ2dHmohOI+egqxQzJo9oHwGfJS1Md/WRO2L+nsHRsNKfZ2E9Ebalu8cIEtSymmDFtYVJYYKMNqDw31aurrd/oDHR5DbbXavZIMtDhzfahe9eyWHZLKr7bQ759/LNw3YTyuamFGquOHcubxtL+8wI8D97e5t9xBURl+9Cd4SPqN2cvUfaDXNX+0GMXbNh6/M6O/1t1RN38WNm4MBjPZ0NYHMWiy3Q/hI0fi80kSUPp6l+JxhC7zdSwlMgV4mg6n5ebBUkx+L/JD9jBBwYMENQDTriMDbBo4Kxk4ugpsz/jzcZAMM7U3ldADhZgzdY7XhoCGTy7ZUdcXR0BELDZW5TkIGdfkgYtyZlz3ARWSU23J2p1YM08GICVDXExPHVmIx
.primevideo.com\tTRUE\t/\tTRUE\t1790306055\tubid-main-av\t260-9405880-5673007
.primevideo.com\tTRUE\t/\tTRUE\t1790306055\tx-main-av\t"IJm8u1LjM7OWEw9FwslJLE9NX7l2CMwXbfgmgX9@KEmy?eKGcsvQxxuNFhlgfZty"
www.primevideo.com\tFALSE\t/\tFALSE\t1789010087\tcsm-hit\ttb:PWT0V8097V6V6WGR46MJ+s-J6AS6PR3KZ5CWA1BQ7CG|1758770087089&t:1758770087089&adb:adblk_no
.primevideo.com\tTRUE\t/\tTRUE\t1793330348\tsession-id\t261-0943717-0251564
.primevideo.com\tTRUE\t/\tFALSE\t1790306532\tav-timezone\tAsia/Calcutta"""

DEFAULT_SERVICES = [
    {
        "id": "hotmail_free",
        "name": "Hotmail / Outlook Free",
        "category": "free",
        "emoji": "📧",
        "description": "Ücretsiz Hotmail / Outlook Mail:Pass Hesaplar"
    },
    {
        "id": "mc_mail_free",
        "name": "Minecraft Mail:Pass",
        "category": "free",
        "emoji": "⛏️",
        "description": "Ücretsiz Minecraft Mail:Pass Hesaplar"
    },
    {
        "id": "netflix_free",
        "name": "Netflix Free",
        "category": "free",
        "emoji": "🎬",
        "description": "Ücretsiz Netflix Hesap Servisi"
    },
    {
        "id": "spotify_free",
        "name": "Spotify Free",
        "category": "free",
        "emoji": "🎧",
        "description": "Ücretsiz Spotify Hesap Servisi"
    },
    {
        "id": "steam_free",
        "name": "Steam Oyunlu (Sınırsız Random)",
        "category": "free",
        "emoji": "🎮",
        "description": "Sınırsız Rastgele Oyunlu Steam Hesapları",
        "is_unlimited": True
    },
    {
        "id": "mailchecker_tool",
        "name": "MailChecker Tool (Ticket)",
        "category": "free",
        "emoji": "🔍",
        "description": "Özel MailChecker Aracına Erişim (Ticket Açılır)",
        "requires_ticket": True
    },
    {
        "id": "iptv_free",
        "name": "IPTV Free (M3U / Xtream)",
        "category": "free",
        "emoji": "📺",
        "description": "Ücretsiz IPTV M3U & Xtream Code Hesapları"
    },
    {
        "id": "exxen_free",
        "name": "Exxen Free",
        "category": "free",
        "emoji": "🎬",
        "description": "Ücretsiz Exxen Hesap Servisi"
    },
    {
        "id": "tod_tv_free",
        "name": "TOD TV Free",
        "category": "free",
        "emoji": "📺",
        "description": "Ücretsiz TOD TV Hesap Servisi (5 Adet Sınırlı Stok)",
        "is_unlimited": False
    },
    {
        "id": "hotmail_vip",
        "name": "Hotmail / Outlook VIP",
        "category": "vip",
        "emoji": "👑",
        "description": "VIP Özel Temiz Hotmail / Outlook Hesapları"
    },
    {
        "id": "mc_vip",
        "name": "Minecraft Premium Full Access",
        "category": "vip",
        "emoji": "💎",
        "description": "VIP Özel Full Access Minecraft Hesap",
        "is_unlimited": True
    },
    {
        "id": "steam_vip",
        "name": "Steam Oyunlu VIP",
        "category": "vip",
        "emoji": "🎮",
        "description": "VIP Özel Oyunlu Steam Hesapları",
        "is_unlimited": False
    },
    {
        "id": "netflix_vip",
        "name": "Netflix UHD 4K",
        "category": "vip",
        "emoji": "📺",
        "description": "VIP Özel Ultra HD 4K Netflix Hesap"
    },
    {
        "id": "iptv_vip",
        "name": "IPTV Premium VIP 4K",
        "category": "vip",
        "emoji": "📡",
        "description": "VIP Özel Donmasız 4K IPTV Üyeliği"
    },
    {
        "id": "exxen_vip",
        "name": "Exxen Premium TV",
        "category": "vip",
        "emoji": "🎬",
        "description": "VIP Özel Exxen Dizi/Film/Spor Üyeliği"
    },
    {
        "id": "tod_tv_vip",
        "name": "TOD TV Premium VIP 4K (Sınırsız)",
        "category": "vip",
        "emoji": "📺",
        "description": "VIP Özel TOD TV Dizi/Film/Spor Üyeliği (Sınırsız)",
        "is_unlimited": True
    },
    {
        "id": "tonguc_vip",
        "name": "Tonguç Akademi VIP (Sınırsız)",
        "category": "vip",
        "emoji": "📚",
        "description": "VIP Özel Tonguç Akademi Hesap (Sınırsız)",
        "is_unlimited": True
    },
    {
        "id": "prime_video_vip",
        "name": "Amazon Prime Video Cookie (Sınırsız)",
        "category": "vip",
        "emoji": "🎬",
        "description": "VIP Özel Prime Video Cookie (Cookie Editor İle Giriş)",
        "is_unlimited": True
    },
    {
        "id": "smm_vip",
        "name": "Cheapest SMM Panels VIP",
        "category": "vip",
        "emoji": "🔑",
        "description": "VIP Özel CheapestSMMPanels Hesabı",
        "is_unlimited": False
    },
    {
        "id": "twitch_vip",
        "name": "Twitch Cookie VIP (Sınırsız)",
        "category": "vip",
        "emoji": "🎮",
        "description": "VIP Özel Twitch Cookie Hesabı (Sınırsız)",
        "is_unlimited": True
    },
    {
        "id": "simmarket_vip",
        "name": "SimMarket VIP (Sınırsız)",
        "category": "vip",
        "emoji": "✈️",
        "description": "VIP Özel SimMarket Hesabı (Sınırsız)",
        "is_unlimited": True
    },
    {
        "id": "gemini_pro",
        "name": "Google Gemini Pro (Sınırsız)",
        "category": "vip",
        "emoji": "🤖",
        "description": "VIP Özel Sınırsız Google Gemini Pro Hesap",
        "is_unlimited": True
    },
    {
        "id": "nitro_promo",
        "name": "Discord Nitro Promo (Ticket)",
        "category": "vip",
        "emoji": "🚀",
        "description": "VIP Özel Discord Nitro Promo (Ticket)",
        "requires_ticket": True
    },
    {
        "id": "spotify_premium_vip",
        "name": "Spotify Premium Bireysel (Ticket)",
        "category": "vip",
        "emoji": "🎧",
        "description": "VIP Özel Spotify Premium Bireysel (Ticket)",
        "requires_ticket": True
    }
]

def _read_json(filepath, default):
    if not os.path.exists(filepath):
        _write_json(filepath, default)
        return default
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[DB HATA] JSON Okuma Hatası ({filepath}): {e}")
        return default

def _write_json(filepath, data):
    try:
        temp_file = filepath + ".tmp"
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(temp_file, filepath)
    except Exception as e:
        print(f"[DB HATA] JSON Yazma Hatası ({filepath}): {e}")

class DatabaseManager:
    def __init__(self):
        self._init_files()

    def _init_files(self):
        with _lock:
            if not os.path.exists(CONFIG_FILE):
                _write_json(CONFIG_FILE, DEFAULT_CONFIG)
            if not os.path.exists(SERVICES_FILE):
                _write_json(SERVICES_FILE, DEFAULT_SERVICES)
            if not os.path.exists(STOCKS_FILE):
                stocks = {s["id"]: [] for s in DEFAULT_SERVICES}
                stocks["gemini_pro"] = ["efe674841@gmail.com:Me261211@"]
                stocks["mc_vip"] = ["retosatis35@outlook.com:Reto2001@"]
                stocks["tonguc_vip"] = ["arslandevrim2@gmail.com:gmailfail098"]
                stocks["tod_tv_free"] = ["emirhankorkut@yahoo.com.tr:2003Emirhan"] * 5
                stocks["tod_tv_vip"] = ["emirhankorkut@yahoo.com.tr:2003Emirhan"]
                stocks["prime_video_vip"] = [PRIME_COOKIE_TEXT]
                stocks["smm_vip"] = ["https://cheapestsmmpanels.com:Anonhax:20112008@"] * 10
                stocks["simmarket_vip"] = ["dimitris9027@hotmail.com:quattro9027"]
                _write_json(STOCKS_FILE, stocks)
            if not os.path.exists(USERS_FILE):
                _write_json(USERS_FILE, {})
            if not os.path.exists(KEYS_FILE):
                _write_json(KEYS_FILE, {})

            services = _read_json(SERVICES_FILE, DEFAULT_SERVICES)
            existing_ids = [s["id"] for s in services]
            for default_s in DEFAULT_SERVICES:
                if default_s["id"] not in existing_ids:
                    services.append(default_s)
            _write_json(SERVICES_FILE, services)

            stocks = _read_json(STOCKS_FILE, {})
            for default_s in DEFAULT_SERVICES:
                if default_s["id"] not in stocks:
                    stocks[default_s["id"]] = []
            _write_json(STOCKS_FILE, stocks)

    # CONFIG MANAGEMENT
    def get_config(self):
        with _lock:
            cfg = _read_json(CONFIG_FILE, DEFAULT_CONFIG)
            for k, v in DEFAULT_CONFIG.items():
                if k not in cfg:
                    cfg[k] = v
            return cfg

    def update_config(self, key, value):
        with _lock:
            cfg = _read_json(CONFIG_FILE, DEFAULT_CONFIG)
            cfg[key] = value
            _write_json(CONFIG_FILE, cfg)
            return cfg

    # SERVICES MANAGEMENT
    def get_services(self, category=None):
        with _lock:
            services = _read_json(SERVICES_FILE, DEFAULT_SERVICES)
            stocks = _read_json(STOCKS_FILE, {})
            changed = False
            for s in services:
                s_id = s.get("id")
                if s_id and s_id not in stocks:
                    stocks[s_id] = []
                    changed = True
            if changed:
                _write_json(STOCKS_FILE, stocks)

            if category:
                return [s for s in services if s.get("category") == category]
            return services

    def get_service(self, service_id):
        with _lock:
            services = _read_json(SERVICES_FILE, DEFAULT_SERVICES)
            for s in services:
                if s["id"] == service_id:
                    return s
            return None

    def add_service(self, service_id, name, category, emoji="🎁", description="", is_unlimited=False, requires_ticket=False):
        with _lock:
            services = _read_json(SERVICES_FILE, DEFAULT_SERVICES)
            for s in services:
                if s["id"] == service_id:
                    s["name"] = name
                    s["category"] = category
                    s["emoji"] = emoji
                    s["description"] = description
                    s["is_unlimited"] = is_unlimited
                    s["requires_ticket"] = requires_ticket
                    _write_json(SERVICES_FILE, services)
                    return False
            
            services.append({
                "id": service_id,
                "name": name,
                "category": category,
                "emoji": emoji,
                "description": description,
                "is_unlimited": is_unlimited,
                "requires_ticket": requires_ticket
            })
            _write_json(SERVICES_FILE, services)

            stocks = _read_json(STOCKS_FILE, {})
            if service_id not in stocks:
                stocks[service_id] = []
                _write_json(STOCKS_FILE, stocks)
            return True

    def delete_service(self, service_id):
        with _lock:
            services = _read_json(SERVICES_FILE, DEFAULT_SERVICES)
            services = [s for s in services if s["id"] != service_id]
            _write_json(SERVICES_FILE, services)

            stocks = _read_json(STOCKS_FILE, {})
            if service_id in stocks:
                del stocks[service_id]
                _write_json(STOCKS_FILE, stocks)
            return True

    # STOCKS MANAGEMENT
    def get_all_stocks(self):
        with _lock:
            return _read_json(STOCKS_FILE, {})

    def get_stock_count(self, service_id):
        with _lock:
            stocks = _read_json(STOCKS_FILE, {})
            return len(stocks.get(service_id, []))

    def add_stock(self, service_id, items):
        with _lock:
            stocks = _read_json(STOCKS_FILE, {})
            if service_id not in stocks:
                stocks[service_id] = []
            
            clean_items = [item.strip() for item in items if item and item.strip()]
            stocks[service_id].extend(clean_items)
            _write_json(STOCKS_FILE, stocks)
            return len(clean_items)

    def clear_stock(self, service_id):
        with _lock:
            stocks = _read_json(STOCKS_FILE, {})
            removed_count = len(stocks.get(service_id, []))
            stocks[service_id] = []
            _write_json(STOCKS_FILE, stocks)
            return removed_count

    def get_stock_account(self, service_id):
        with _lock:
            stocks = _read_json(STOCKS_FILE, {})
            services = _read_json(SERVICES_FILE, DEFAULT_SERVICES)
            service = None
            for s in services:
                if s["id"] == service_id:
                    service = s
                    break

            if service_id in ["mailchecker_tool", "spotify_premium_vip"] or (service and service.get("requires_ticket")):
                return "TICKET_CREATED"

            if service_id not in stocks or len(stocks[service_id]) == 0:
                return None

            is_unlimited = (service_id in ["steam_free", "gemini_pro", "mc_vip", "tonguc_vip", "tod_tv_vip", "prime_video_vip", "twitch_vip", "simmarket_vip"]) or (service and service.get("is_unlimited", False))

            if is_unlimited:
                return random.choice(stocks[service_id])
            else:
                account = stocks[service_id].pop(0)
                _write_json(STOCKS_FILE, stocks)
                return account

    # USER & VIP & INVITES & MESSAGE ACTIVITY MANAGEMENT
    def get_user_data(self, user_id):
        user_str = str(user_id)
        with _lock:
            users = _read_json(USERS_FILE, {})
            if user_str not in users:
                users[user_str] = {
                    "is_vip": False,
                    "vip_expires": 0,
                    "claims": [],
                    "total_claims": 0,
                    "last_claim_timestamp": 0,
                    "daily_claims": [],
                    "last_wheel_spin": 0,
                    "invites": 0,
                    "message_count": 0,
                    "invited_by": None
                }
            return users[user_str]

    def record_user_message(self, user_id):
        user_str = str(user_id)
        with _lock:
            users = _read_json(USERS_FILE, {})
            if user_str not in users:
                users[user_str] = {
                    "is_vip": False,
                    "vip_expires": 0,
                    "claims": [],
                    "total_claims": 0,
                    "last_claim_timestamp": 0,
                    "daily_claims": [],
                    "last_wheel_spin": 0,
                    "invites": 0,
                    "message_count": 1,
                    "invited_by": None
                }
            else:
                users[user_str]["message_count"] = users[user_str].get("message_count", 0) + 1
            _write_json(USERS_FILE, users)

    def has_user_chatted(self, user_id) -> bool:
        user_str = str(user_id)
        with _lock:
            users = _read_json(USERS_FILE, {})
            u = users.get(user_str, {})
            return u.get("message_count", 0) > 0

    def add_user_invite(self, inviter_id):
        inviter_str = str(inviter_id)
        with _lock:
            users = _read_json(USERS_FILE, {})
            if inviter_str not in users:
                users[inviter_str] = {
                    "is_vip": False,
                    "vip_expires": 0,
                    "claims": [],
                    "total_claims": 0,
                    "last_claim_timestamp": 0,
                    "daily_claims": [],
                    "last_wheel_spin": 0,
                    "invites": 1,
                    "message_count": 0,
                    "invited_by": None
                }
            else:
                users[inviter_str]["invites"] = users[inviter_str].get("invites", 0) + 1
            
            cfg = self.get_config()
            target_invites = cfg.get("invites_for_vip", 5)
            if users[inviter_str]["invites"] >= target_invites:
                users[inviter_str]["is_vip"] = True
                users[inviter_str]["vip_expires"] = time.time() + (24 * 3600)

            _write_json(USERS_FILE, users)
            return users[inviter_str]["invites"]

    def set_user_vip(self, user_id, is_vip: bool, duration_hours: int = 0):
        user_str = str(user_id)
        with _lock:
            users = _read_json(USERS_FILE, {})
            u = users.get(user_str, {
                "is_vip": False,
                "vip_expires": 0,
                "claims": [],
                "total_claims": 0,
                "last_claim_timestamp": 0,
                "daily_claims": [],
                "last_wheel_spin": 0,
                "invites": 0,
                "message_count": 0
            })
            u["is_vip"] = is_vip
            if is_vip and duration_hours > 0:
                u["vip_expires"] = time.time() + (duration_hours * 3600)
            else:
                u["vip_expires"] = 0
            users[user_str] = u
            _write_json(USERS_FILE, users)

    def is_user_vip_db(self, user_id):
        user_str = str(user_id)
        with _lock:
            users = _read_json(USERS_FILE, {})
            u = users.get(user_str, {})
            if not u.get("is_vip", False):
                return False
            expires = u.get("vip_expires", 0)
            if expires > 0 and time.time() > expires:
                u["is_vip"] = False
                u["vip_expires"] = 0
                _write_json(USERS_FILE, users)
                return False
            return True

    def check_user_cooldown(self, user_id, is_vip=False, is_booster=False):
        user_str = str(user_id)
        config = self.get_config()
        cooldown_hours = config.get("cooldown_hours", 24)
        
        if is_booster:
            daily_limit = config.get("booster_daily_limit", 3)
        elif is_vip:
            daily_limit = config.get("vip_daily_limit", 2)
        else:
            daily_limit = config.get("free_daily_limit", 1)

        with _lock:
            users = _read_json(USERS_FILE, {})
            u = users.get(user_str, {
                "is_vip": False,
                "claims": [],
                "total_claims": 0,
                "last_claim_timestamp": 0,
                "daily_claims": []
            })

            now = time.time()
            cooldown_seconds = cooldown_hours * 3600

            recent_claims = [t for t in u.get("daily_claims", []) if now - t < cooldown_seconds]
            claims_count = len(recent_claims)

            if claims_count >= daily_limit:
                oldest_recent_claim = min(recent_claims)
                time_passed = now - oldest_recent_claim
                remaining_sec = max(0, cooldown_seconds - time_passed)
                return False, remaining_sec, claims_count, daily_limit

            return True, 0, claims_count, daily_limit

    def record_claim(self, user_id, service_id, account_data, is_vip=False):
        user_str = str(user_id)
        config = self.get_config()
        cooldown_seconds = config.get("cooldown_hours", 24) * 3600

        with _lock:
            users = _read_json(USERS_FILE, {})
            if user_str not in users:
                users[user_str] = {
                    "is_vip": False,
                    "claims": [],
                    "total_claims": 0,
                    "last_claim_timestamp": 0,
                    "daily_claims": []
                }
            
            now = time.time()
            u = users[user_str]
            
            u["daily_claims"] = [t for t in u.get("daily_claims", []) if now - t < cooldown_seconds]
            u["daily_claims"].append(now)
            u["last_claim_timestamp"] = now
            u["total_claims"] = u.get("total_claims", 0) + 1
            
            u.setdefault("claims", []).append({
                "service_id": service_id,
                "account": account_data,
                "timestamp": now,
                "is_vip": is_vip
            })

            _write_json(USERS_FILE, users)

    def reset_user_cooldown(self, user_id):
        user_str = str(user_id)
        with _lock:
            users = _read_json(USERS_FILE, {})
            if user_str in users:
                users[user_str]["daily_claims"] = []
                users[user_str]["last_claim_timestamp"] = 0
                _write_json(USERS_FILE, users)
                return True
            return False

    # DAILY WHEEL SPIN
    def check_user_wheel_spin(self, user_id):
        user_str = str(user_id)
        with _lock:
            users = _read_json(USERS_FILE, {})
            u = users.get(user_str, {})
            last_spin = u.get("last_wheel_spin", 0)
            now = time.time()
            cooldown_sec = 24 * 3600
            if now - last_spin < cooldown_sec:
                return False, cooldown_sec - (now - last_spin)
            return True, 0

    def record_wheel_spin(self, user_id):
        user_str = str(user_id)
        with _lock:
            users = _read_json(USERS_FILE, {})
            if user_str not in users:
                users[user_str] = {"last_wheel_spin": time.time()}
            else:
                users[user_str]["last_wheel_spin"] = time.time()
            _write_json(USERS_FILE, users)

    # REMINDER SYSTEM (COOLDOWN REFRESHED / AVAILABLE USERS)
    def get_eligible_reminder_users(self):
        with _lock:
            users = _read_json(USERS_FILE, {})
            eligible = []
            now = time.time()
            config = self.get_config()
            cooldown_seconds = config.get("cooldown_hours", 24) * 3600

            for u_id_str, u_data in users.items():
                # Check last reminder timestamp (minimum 24 hours between reminders)
                last_reminder = u_data.get("last_reminder_sent", 0)
                if now - last_reminder < (24 * 3600):
                    continue

                # Check if user has available claim limit right now
                daily_claims = u_data.get("daily_claims", [])
                recent_claims = [t for t in daily_claims if now - t < cooldown_seconds]
                
                is_vip = u_data.get("is_vip", False)
                daily_limit = config.get("vip_daily_limit", 2) if is_vip else config.get("free_daily_limit", 1)

                # Eligible if they have unused daily limits
                if len(recent_claims) < daily_limit:
                    eligible.append(int(u_id_str))

            return eligible

    def record_reminder_sent(self, user_id):
        user_str = str(user_id)
        with _lock:
            users = _read_json(USERS_FILE, {})
            if user_str in users:
                users[user_str]["last_reminder_sent"] = time.time()
                _write_json(USERS_FILE, users)

    def get_all_users_claim_status(self):
        with _lock:
            users = _read_json(USERS_FILE, {})
            config = self.get_config()
            cooldown_hours = config.get("cooldown_hours", 24)
            cooldown_seconds = cooldown_hours * 3600
            now = time.time()

            result = []
            for user_id, u_data in users.items():
                is_vip = u_data.get("is_vip", False)
                vip_expires = u_data.get("vip_expires", 0)
                if vip_expires > 0 and now > vip_expires:
                    is_vip = False

                daily_limit = config.get("vip_daily_limit", 2) if is_vip else config.get("free_daily_limit", 1)
                recent_claims = [t for t in u_data.get("daily_claims", []) if now - t < cooldown_seconds]
                claims_count = len(recent_claims)
                remaining_rights = max(0, daily_limit - claims_count)

                remaining_sec = 0
                if claims_count >= daily_limit and recent_claims:
                    oldest = min(recent_claims)
                    remaining_sec = max(0, cooldown_seconds - (now - oldest))

                result.append({
                    "user_id": user_id,
                    "is_vip": is_vip,
                    "vip_expires": vip_expires,
                    "claims_count": claims_count,
                    "daily_limit": daily_limit,
                    "remaining_rights": remaining_rights,
                    "remaining_sec": remaining_sec,
                    "total_claims": u_data.get("total_claims", 0),
                    "invites": u_data.get("invites", 0),
                    "message_count": u_data.get("message_count", 0),
                    "last_claim_timestamp": u_data.get("last_claim_timestamp", 0),
                    "claims": u_data.get("claims", [])
                })

            result.sort(key=lambda x: (x["remaining_rights"], x["total_claims"]), reverse=True)
            return result

    # PROMO KEYS & ADVANCED COUPON SYSTEM
    def create_coupon(self, code: str, reward_type: str, reward_value: str = "24", max_uses: int = 1, specific_service: str = ""):
        code = code.strip().upper()
        with _lock:
            keys = _read_json(KEYS_FILE, {})
            keys[code] = {
                "code": code,
                "reward_type": reward_type, # 'vip', 'claim', 'steam', 'service'
                "reward_value": reward_value,
                "max_uses": max_uses,
                "used_count": 0,
                "used_by": [], # list of user_id strings
                "specific_service": specific_service,
                "created_at": time.time()
            }
            _write_json(KEYS_FILE, keys)
            return keys[code]

    def get_all_coupons(self):
        with _lock:
            return _read_json(KEYS_FILE, {})

    def delete_coupon(self, code: str):
        code = code.strip().upper()
        with _lock:
            keys = _read_json(KEYS_FILE, {})
            if code in keys:
                del keys[code]
                _write_json(KEYS_FILE, keys)
                return True
            return False

    def redeem_coupon(self, user_id, username: str, code: str):
        code = code.strip().upper()
        user_str = str(user_id)
        with _lock:
            keys = _read_json(KEYS_FILE, {})
            if code not in keys:
                return False, "❌ **Geçersiz Kupon Kodu!** Lütfen kodu doğru yazdığınızdan emin olun.", None

            coupon = keys[code]
            used_by = coupon.get("used_by", [])
            max_uses = coupon.get("max_uses", 1)
            used_count = coupon.get("used_count", len(used_by))

            if user_str in used_by:
                return False, "⚠️ **Bu kuponu zaten daha önce kullandınız!** Her üye bir kupondan yalnızca 1 kez faydalanabilir.", None

            if used_count >= max_uses:
                return False, "❌ **Kuponun Kullanım Kotası Doldu!** Bu kupon belirlenen maksimum kişi sayısına ulaştı.", None

            reward_type = coupon.get("reward_type", "claim")
            reward_value = coupon.get("reward_value", "24")
            extra_account = None

            if reward_type == "vip":
                try:
                    hours = int(reward_value)
                except Exception:
                    hours = 24
                self.set_user_vip(user_id, True, duration_hours=hours)
                days_txt = f"{hours // 24} Günlük" if hours >= 24 and hours % 24 == 0 else f"{hours} Saatlik"
                msg = f"⭐ Tebrikler! Hesabınıza **{days_txt} VIP Üyelik** tanımlandı! Hemen VIP servislerden stok alabilirsiniz. 🚀"

            elif reward_type == "claim":
                self.reset_user_cooldown(user_id)
                msg = "🎁 Tebrikler! **+1 Ekstra Stok Hakkı** kazandınız (Günlük bekleme süreniz sıfırlandı)!"

            elif reward_type == "steam":
                acc = self.get_stock_account("steam_free")
                if acc:
                    extra_account = acc
                    msg = f"🎮 Tebrikler! **Oyunlu Steam Hesabı** kazandınız!\n\n**🔑 Hesap Bilgisi:**\n```\n{acc}\n```"
                else:
                    msg = "🎮 Tebrikler! Steam hesabınız stoklar yenilendiğinde teslim edilecektir."

            elif reward_type == "service":
                serv_id = coupon.get("specific_service", "netflix_free")
                serv = self.get_service(serv_id)
                serv_name = serv["name"] if serv else serv_id
                acc = self.get_stock_account(serv_id)
                if acc:
                    extra_account = acc
                    msg = f"🎉 Tebrikler! **{serv_name}** hesabınız hazır!\n\n**🔑 Hesap / Link Bilgisi:**\n```\n{acc}\n```"
                else:
                    msg = f"🎉 Tebrikler! **{serv_name}** hakkı kazandınız. (Stok yenilendiğinde teslim edilecektir)"
            else:
                msg = "✅ Kupon başarıyla tanımlandı!"

            # Record usage
            used_by.append(user_str)
            coupon["used_by"] = used_by
            coupon["used_count"] = len(used_by)
            _write_json(KEYS_FILE, keys)

            # Log event
            self.add_event_log(
                event_type="COUPON",
                user_id=user_id,
                username=username,
                title=f"Kupon Kodu Kullandı: {code}",
                details=f"Ödül: {reward_type} | Kalan Kota: {max_uses - len(used_by)}/{max_uses}",
                service_id=code
            )

            return True, msg, extra_account

    # EVENT LOGS SYSTEM (ADMIN ONLY)
    def add_event_log(self, event_type: str, user_id: int, username: str, title: str, details: str, service_id: str = ""):
        with _lock:
            logs = _read_json(LOGS_FILE, [])
            log_entry = {
                "id": len(logs) + 1,
                "event_type": event_type, # 'CLAIM', 'WHEEL', 'VIP', 'RESTOCK', 'REMINDER', 'KEY'
                "user_id": str(user_id),
                "username": username,
                "title": title,
                "details": details,
                "service_id": service_id,
                "timestamp": time.time()
            }
            logs.insert(0, log_entry)
            # Keep latest 500 logs to prevent file bloat
            if len(logs) > 500:
                logs = logs[:500]
            _write_json(LOGS_FILE, logs)
            return log_entry

    def get_recent_logs(self, limit: int = 15, event_type: str = None):
        with _lock:
            logs = _read_json(LOGS_FILE, [])
            if event_type:
                filtered = [l for l in logs if l.get("event_type") == event_type]
                return filtered[:limit]
            return logs[:limit]

    # LEADERBOARD
    def get_leaderboard(self, limit=10):
        with _lock:
            users = _read_json(USERS_FILE, {})
            user_list = []
            for u_id, u_data in users.items():
                user_list.append({
                    "user_id": u_id,
                    "claims": u_data.get("total_claims", 0),
                    "invites": u_data.get("invites", 0),
                    "is_vip": u_data.get("is_vip", False)
                })
            user_list.sort(key=lambda x: x["claims"], reverse=True)
            return user_list[:limit]

    # ADMIN STATS REPORT
    def get_admin_stats(self):
        with _lock:
            users = _read_json(USERS_FILE, {})
            services = _read_json(SERVICES_FILE, DEFAULT_SERVICES)
            stocks = _read_json(STOCKS_FILE, {})

            total_services = len(services)
            total_current_stock = sum(len(stk) for stk in stocks.values())
            
            total_claims_all_time = 0
            total_registered_users = len(users)
            total_vip_users = 0
            total_invites = 0
            chatted_users_count = 0

            service_claims_count = {}

            for u_id, u_data in users.items():
                t_claims = u_data.get("total_claims", 0)
                total_claims_all_time += t_claims
                if u_data.get("is_vip", False):
                    total_vip_users += 1
                total_invites += u_data.get("invites", 0)
                if u_data.get("message_count", 0) > 0:
                    chatted_users_count += 1

                for claim in u_data.get("claims", []):
                    s_id = claim.get("service_id")
                    if s_id:
                        service_claims_count[s_id] = service_claims_count.get(s_id, 0) + 1

            most_claimed_service = "Henüz Yok"
            if service_claims_count:
                top_s_id = max(service_claims_count, key=service_claims_count.get)
                top_s = self.get_service(top_s_id)
                top_name = top_s["name"] if top_s else top_s_id
                most_claimed_service = f"{top_name} ({service_claims_count[top_s_id]} kez)"

            return {
                "total_services": total_services,
                "total_current_stock": total_current_stock,
                "total_claims_all_time": total_claims_all_time,
                "total_registered_users": total_registered_users,
                "total_vip_users": total_vip_users,
                "total_invites": total_invites,
                "chatted_users_count": chatted_users_count,
                "most_claimed_service": most_claimed_service
            }

db = DatabaseManager()
