import os
import sys
import time
import asyncio
import random
from datetime import datetime, timezone
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from aiohttp import web

# Fix Windows console UTF-8 printing
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from database import db

# Load environment variables
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = os.getenv("GUILD_ID")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True
intents.invites = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Track Bot Start Time for Uptime
BOT_START_TIME = time.time()

# Global Invites Cache
invites_cache = {}

# --- KEEP-ALIVE WEB SERVER FOR RENDER & BETTERSTACK ---
async def handle_ping(request):
    return web.Response(
        text="<html><body><h1>🤖 LeaksTr Discord Bot 7/24 Aktif ve Çalışıyor!</h1><p>BetterStack / Uptime Robot Ping OK ✅</p></body></html>",
        content_type="text/html"
    )

async def start_web_server():
    try:
        app = web.Application()
        app.router.add_get("/", handle_ping)
        app.router.add_get("/health", handle_ping)
        app.router.add_get("/ping", handle_ping)

        port = int(os.getenv("PORT", 10000))
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", port)
        await site.start()
        print(f"🌐 Keep-Alive Web Sunucusu 0.0.0.0:{port} Üzerinde Başlatıldı! BetterStack İle Uyumlu.")
    except Exception as e:
        print(f"⚠️ Web Sunucusu Başlatma Hatası: {e}")

# --- HELPER FUNCTIONS ---
def is_booster_user(member: discord.Member) -> bool:
    if not isinstance(member, discord.Member):
        return False
    return member.premium_since is not None

def is_vip_user(member: discord.Member) -> bool:
    if not isinstance(member, discord.Member):
        return False
    if member.guild_permissions.administrator:
        return True
    if is_booster_user(member):
        return True
    if db.is_user_vip_db(member.id):
        return True
    config = db.get_config()
    vip_role_id = config.get("vip_role_id", 0)
    if vip_role_id and any(r.id == int(vip_role_id) for r in member.roles):
        return True
    return any("vip" in r.name.lower() for r in member.roles)

def is_admin_user(member: discord.Member) -> bool:
    if not isinstance(member, discord.Member):
        return False
    if member.guild_permissions.administrator:
        return True
    config = db.get_config()
    admin_role_id = config.get("admin_role_id", 0)
    if admin_role_id and any(r.id == int(admin_role_id) for r in member.roles):
        return True
    return False

def check_user_custom_status(member: discord.Member) -> bool:
    """Checks if member has 'LeaksTr' (or configured text) in their Discord Custom Status."""
    if not isinstance(member, discord.Member):
        return True
    if member.guild_permissions.administrator:
        return True

    config = db.get_config()
    required = config.get("required_status", "LeaksTr").strip().lower()
    if not required:
        return True

    for act in member.activities:
        if isinstance(act, discord.CustomActivity):
            if act.name and required in act.name.lower():
                return True
            if act.state and required in act.state.lower():
                return True
    return False

def check_user_chat_activity(member: discord.Member) -> bool:
    """Checks if member has sent at least 1 message in the server."""
    if not isinstance(member, discord.Member):
        return True
    if member.guild_permissions.administrator:
        return True
    return db.has_user_chatted(member.id)

def check_anti_alt(member: discord.Member) -> tuple[bool, int]:
    """Checks if member's Discord account age is older than minimum days (Anti-Alt)."""
    if not isinstance(member, discord.Member):
        return True, 999
    if member.guild_permissions.administrator:
        return True, 999

    config = db.get_config()
    min_days = config.get("min_account_age_days", 7)
    
    created_at = member.created_at
    now = datetime.now(timezone.utc)
    age_days = (now - created_at).days

    if age_days < min_days:
        return False, age_days
    return True, age_days

def format_seconds(seconds: float) -> str:
    seconds = int(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    parts = []
    if hours > 0:
        parts.append(f"{hours} saat")
    if minutes > 0:
        parts.append(f"{minutes} dakika")
    if secs > 0 or len(parts) == 0:
        parts.append(f"{secs} saniye")
    return " ".join(parts)

async def log_claim(guild: discord.Guild, user: discord.User, service: dict, account_data: str, is_vip: bool):
    config = db.get_config()
    channel_id = config.get("log_channel_id", 0) or os.getenv("LOG_CHANNEL_ID", 0)
    if not channel_id:
        return
    
    try:
        channel = guild.get_channel(int(channel_id))
        if channel:
            embed = discord.Embed(
                title="📥 Yeni Stok Teslimatı!",
                color=discord.Color.gold() if is_vip else discord.Color.green(),
                timestamp=discord.utils.utcnow()
            )
            embed.add_field(name="👤 Kullanıcı", value=f"{user.mention} (`{user.id}`)", inline=True)
            embed.add_field(name="📦 Servis", value=f"{service.get('emoji', '🎁')} **{service.get('name')}**", inline=True)
            embed.add_field(name="👑 Üyelik Türü", value="⭐ VIP" if is_vip else "🎁 Free", inline=True)
            
            is_unlimited = service.get("id") in ["steam_free", "gemini_pro", "mc_vip", "tonguc_vip", "tod_tv_vip", "prime_video_vip"] or service.get("is_unlimited", False)
            stk_txt = "∞ Sınırsız" if is_unlimited else f"{db.get_stock_count(service['id'])} adet"
            embed.set_footer(text=f"Kalan Stok: {stk_txt}")
            await channel.send(embed=embed)
    except Exception as e:
        print(f"[LOG HATA] Log kanalına mesaj gönderilemedi: {e}")


# --- TICKET CLOSE VIEW ---
class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔒 Ticket'ı Kapat", style=discord.ButtonStyle.danger, custom_id="btn_close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🔒 **Bu Ticket 5 saniye içinde kapatılıp silinecektir...**")
        await asyncio.sleep(5)
        try:
            await interaction.channel.delete()
        except Exception as e:
            print(f"Ticket silme hatası: {e}")


# --- COIN MARKET VIEW ---
class CoinMarketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)

    @discord.ui.button(label="🎧 100 Coin İle Spotify Premium Al (Ticket)", style=discord.ButtonStyle.primary, emoji="🎧")
    async def buy_spotify_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        user = interaction.user
        guild = interaction.guild

        if not guild:
            await interaction.followup.send("❌ Bu işlem sadece sunucu içerisinde yapılabilir.", ephemeral=True)
            return

        user_id = user.id

        # Deduct 100 Coins
        success = db.remove_user_coins(user_id, 100)
        if not success:
            u_data = db.get_user_data(user_id)
            current_coins = u_data.get("coins", 0)
            embed = discord.Embed(
                title="❌ Yetersiz Coin Bakiyesi!",
                description=f"Spotify Premium Bireysel almak için **100 Coin** gereklidir.\n\n📌 **Mevcut Bakiyeniz:** `{current_coins} Coin`",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        channel_name = f"🎧-spotify-premium-{user.name[:10]}".lower().replace(" ", "-")
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, attach_files=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_channels=True)
        }

        cfg = db.get_config()
        admin_role_id = cfg.get("admin_role_id", 0)
        if admin_role_id:
            admin_role = guild.get_role(int(admin_role_id))
            if admin_role:
                overwrites[admin_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True)

        try:
            ticket_channel = await guild.create_text_channel(
                name=channel_name,
                overwrites=overwrites,
                topic=f"100 Coin Spotify Premium Bireysel Talebi - {user.name} ({user.id})"
            )

            u_data = db.get_user_data(user_id)
            ticket_embed = discord.Embed(
                title="🎧 Spotify Premium Bireysel Talebi Alındı! (100 Coin)",
                description=(
                    f"Merhaba {user.mention}!\n\n"
                    f"Hesabınızdan **100 Coin** başarıyla düşüldü (Kalan Bakiyeniz: `{u_data.get('coins', 0)} Coin`).\n\n"
                    f"📌 **Spotify Premium Bireysel** davet/hesap talebiniz yetkililerimize iletildi.\n"
                    f"Adminlerimiz (Efe / Yetkili) en kısa sürede **size özel Spotify Premium davet linkinizi veya hesabınızı** "
                    f"bu kanala manuel olarak teslim edecektir.\n\n"
                    f"⏱️ Lütfen bekleyin ve kanal bildirimlerinizi açık tutun!"
                ),
                color=discord.Color.green(),
                timestamp=discord.utils.utcnow()
            )
            ticket_embed.set_footer(text="İşleminiz bittiğinde aşağıdaki '🔒 Ticket'ı Kapat' butonuna basabilirsiniz.")
            
            await ticket_channel.send(content=f"🔔 {user.mention} @here", embed=ticket_embed, view=CloseTicketView())

            db.record_claim(user_id, "spotify_premium_vip", f"TICKET: #{ticket_channel.name} (100 Coin)", is_vip=True)

            success_embed = discord.Embed(
                title="🎫 Spotify Premium Ticket Kanalınız Açıldı!",
                description=f"**100 Coin** düşüldü ve talebiniz için özel kanal oluşturuldu:\n👉 {ticket_channel.mention}\n\nLütfen kanala giderek yetkilimizin size özel Spotify Premium linkinizi/hesabınızı vermesini bekleyin.",
                color=discord.Color.green()
            )
            await interaction.followup.send(embed=success_embed, ephemeral=True)

        except Exception as e:
            db.add_user_coins(user_id, 100) # Refund
            await interaction.followup.send(f"❌ Ticket kanalı açılırken hata oluştu: {e}. 100 Coin bakiyeniz iade edildi.", ephemeral=True)

    @discord.ui.button(label="🤖 50 Coin İle Gemini Pro Al", style=discord.ButtonStyle.success, emoji="🤖")
    async def buy_gemini_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        user_id = interaction.user.id
        
        success = db.remove_user_coins(user_id, 50)
        if not success:
            u_data = db.get_user_data(user_id)
            current_coins = u_data.get("coins", 0)
            embed = discord.Embed(
                title="❌ Yetersiz Coin Bakiyesi!",
                description=f"Google Gemini Pro almak için **50 Coin** gereklidir.\n\n📌 **Mevcut Bakiyeniz:** `{current_coins} Coin`",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        account_data = db.get_stock_account("gemini_pro")
        if not account_data:
            db.add_user_coins(user_id, 50) # Refund
            await interaction.followup.send("❌ Stok çekilirken hata oluştu. 50 Coin bakiyeniz iade edildi.", ephemeral=True)
            return

        u_data = db.get_user_data(user_id)
        embed = discord.Embed(
            title="🤖 Google Gemini Pro Hesabı Teslim Edildi!",
            description=f"Hesabınızdan **50 Coin** düşüldü ve Gemini Pro hesabınız teslim edildi! 🚀\n\n📌 **Kalan Bakiyeniz:** `{u_data.get('coins', 0)} Coin`",
            color=discord.Color.green()
        )
        embed.add_field(name="🔑 Google Gemini Pro Hesap (Mail:Şifre)", value=f"```\n{account_data}\n```", inline=False)
        embed.set_footer(text="LeaksTr Coin Market • Sınırsız Random Stok • 7/24 Otomatik Teslimat")
        await interaction.followup.send(embed=embed, ephemeral=True)

    @discord.ui.button(label="🚀 100 Coin İle Nitro Promo Al (Ticket)", style=discord.ButtonStyle.primary, emoji="🚀")
    async def buy_nitro_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        user = interaction.user
        guild = interaction.guild

        if not guild:
            await interaction.followup.send("❌ Bu işlem sadece sunucu içerisinde yapılabilir.", ephemeral=True)
            return

        user_id = user.id

        # Deduct 100 Coins
        success = db.remove_user_coins(user_id, 100)
        if not success:
            u_data = db.get_user_data(user_id)
            current_coins = u_data.get("coins", 0)
            embed = discord.Embed(
                title="❌ Yetersiz Coin Bakiyesi!",
                description=f"Discord Nitro Promo almak için **100 Coin** gereklidir.\n\n📌 **Mevcut Bakiyeniz:** `{current_coins} Coin`",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        channel_name = f"🚀-nitro-promo-{user.name[:10]}".lower().replace(" ", "-")
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, attach_files=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_channels=True)
        }

        cfg = db.get_config()
        admin_role_id = cfg.get("admin_role_id", 0)
        if admin_role_id:
            admin_role = guild.get_role(int(admin_role_id))
            if admin_role:
                overwrites[admin_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True)

        try:
            ticket_channel = await guild.create_text_channel(
                name=channel_name,
                overwrites=overwrites,
                topic=f"100 Coin Discord Nitro Promo Talebi - {user.name} ({user.id})"
            )

            u_data = db.get_user_data(user_id)
            ticket_embed = discord.Embed(
                title="🚀 Discord Nitro Promo Talebi Alındı! (100 Coin)",
                description=(
                    f"Merhaba {user.mention}!\n\n"
                    f"Hesabınızdan **100 Coin** başarıyla düşüldü (Kalan Bakiyeniz: `{u_data.get('coins', 0)} Coin`).\n\n"
                    f"📌 **Discord Nitro Promo** talebiniz yetkililerimize iletildi.\n"
                    f"Adminlerimiz (Efe / Yetkili) en kısa sürede **size özel çalışan Nitro Promo linkinizi/kodunuzu** "
                    f"bu kanala manuel olarak teslim edecektir.\n\n"
                    f"⏱️ Lütfen bekleyin ve kanal bildirimlerinizi açık tutun!"
                ),
                color=discord.Color.purple(),
                timestamp=discord.utils.utcnow()
            )
            ticket_embed.set_footer(text="İşleminiz bittiğinde aşağıdaki '🔒 Ticket'ı Kapat' butonuna basabilirsiniz.")
            
            await ticket_channel.send(content=f"🔔 {user.mention} @here", embed=ticket_embed, view=CloseTicketView())

            db.record_claim(user_id, "nitro_promo", f"TICKET: #{ticket_channel.name} (100 Coin)", is_vip=True)

            success_embed = discord.Embed(
                title="🎫 Nitro Promo Ticket Kanalınız Açıldı!",
                description=f"**100 Coin** düşüldü ve talebiniz için özel kanal oluşturuldu:\n👉 {ticket_channel.mention}\n\nLütfen kanala giderek yetkilimizin size özel Nitro Promo kodunuzu vermesini bekleyin.",
                color=discord.Color.green()
            )
            await interaction.followup.send(embed=success_embed, ephemeral=True)

        except Exception as e:
            db.add_user_coins(user_id, 100)
            await interaction.followup.send(f"❌ Ticket kanalı açılırken bir hata oluştu: {e}. 100 Coin bakiyeniz hesabınıza iade edildi.", ephemeral=True)

    @discord.ui.button(label="⭐ 20 Coin İle 24 Sa VIP Al", style=discord.ButtonStyle.secondary, emoji="👑")
    async def buy_vip_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        user_id = interaction.user.id
        
        success = db.remove_user_coins(user_id, 20)
        if not success:
            u_data = db.get_user_data(user_id)
            current_coins = u_data.get("coins", 0)
            embed = discord.Embed(
                title="❌ Yetersiz Coin Bakiyesi!",
                description=f"VIP üyelik almak için **20 Coin** gereklidir.\n\n📌 **Mevcut Bakiyeniz:** `{current_coins} Coin`",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        db.set_user_vip(user_id, True, duration_hours=24)
        u_data = db.get_user_data(user_id)
        embed = discord.Embed(
            title="🎉 VIP Üyelik Satın Alındı!",
            description=f"Hesabınızdan **20 Coin** düşüldü ve **24 Saatlik VIP Üyelik** tanımlandı! 🚀\n\n📌 **Kalan Bakiyeniz:** `{u_data.get('coins', 0)} Coin`",
            color=discord.Color.gold()
        )
        await interaction.followup.send(embed=embed, ephemeral=True)

    @discord.ui.button(label="🎁 20 Coin İle +1 Stok Hakkı Al", style=discord.ButtonStyle.secondary, emoji="⚡")
    async def buy_claim_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        user_id = interaction.user.id
        
        success = db.remove_user_coins(user_id, 20)
        if not success:
            u_data = db.get_user_data(user_id)
            current_coins = u_data.get("coins", 0)
            embed = discord.Embed(
                title="❌ Yetersiz Coin Bakiyesi!",
                description=f"Ekstra stok hakkı almak için **20 Coin** gereklidir.\n\n📌 **Mevcut Bakiyeniz:** `{current_coins} Coin`",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        db.reset_user_cooldown(user_id)
        u_data = db.get_user_data(user_id)
        embed = discord.Embed(
            title="🎉 Ekstra Stok Hakkı Satın Alındı!",
            description=f"Hesabınızdan **20 Coin** düşüldü ve bekleme süreniz sıfırlandı! Hemen stok alabilirsiniz. 🎁\n\n📌 **Kalan Bakiyeniz:** `{u_data.get('coins', 0)} Coin`",
            color=discord.Color.green()
        )
        await interaction.followup.send(embed=embed, ephemeral=True)


# --- ADMIN MODALS & SELECTS ---

class AddStockModal(discord.ui.Modal, title="📦 Servise Stok Ekle"):
    def __init__(self, service_id: str, service_name: str):
        super().__init__()
        self.service_id = service_id
        self.service_name = service_name
        
        self.stock_input = discord.ui.TextInput(
            label=f"{service_name} Hesapları / Kodları",
            style=discord.TextStyle.paragraph,
            placeholder="Her satıra 1 hesap gelecek şekilde yapıştırın:\nemail:şifre\nemail:şifre:extra",
            required=True,
            max_length=4000
        )
        self.add_item(self.stock_input)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        lines = self.stock_input.value.strip().split("\n")
        added_count = db.add_stock(self.service_id, lines)
        total_stock = db.get_stock_count(self.service_id)
        
        embed = discord.Embed(
            title="✅ Stok Başarıyla Eklendi",
            description=f"**{self.service_name}** servisine **{added_count}** adet hesap/kod eklendi!\nGüncel Toplam Stok: **{total_stock}** adet",
            color=discord.Color.green()
        )
        await interaction.followup.send(embed=embed, ephemeral=True)


class RestockAnnouncementModal(discord.ui.Modal, title="📢 Stok Yenileme Duyurusu Yap"):
    announcement_title = discord.ui.TextInput(
        label="Duyuru Başlığı",
        placeholder="Örn: HUGE RESTOCK! Netflix ve Minecraft Stokları Yenilendi! 🚀",
        default="🔥 STOKLAR YENİLENDİ!",
        required=True
    )
    announcement_content = discord.ui.TextInput(
        label="Duyuru Metni",
        style=discord.TextStyle.paragraph,
        placeholder="Duyuru detaylarını buraya yazın...",
        default="Değerli üyelerimiz, beklenen tüm Free ve VIP stoklarımız başarıyla güncellenmiştir! Aşağıdaki butonlardan hesaplarınızı alabilirsiniz.",
        required=True
    )
    ping_type = discord.ui.TextInput(
        label="Etiketleme (everyone / here / none)",
        placeholder="everyone, here veya none yazın",
        default="here",
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        embed = discord.Embed(
            title=self.announcement_title.value,
            description=self.announcement_content.value,
            color=discord.Color.gold(),
            timestamp=discord.utils.utcnow()
        )
        embed.add_field(
            name="📊 Güncel Stok Özeti",
            value="Aşağıdaki butonları kullanarak hemen stok alabilirsiniz!",
            inline=False
        )
        embed.set_footer(text=f"Duyuru Yapan: {interaction.user.name}")

        ping_str = ""
        p_val = self.ping_type.value.strip().lower()
        if p_val == "everyone":
            ping_str = "@everyone"
        elif p_val == "here":
            ping_str = "@here"

        await interaction.channel.send(content=ping_str, embed=embed, view=MainPanelView())
        await interaction.followup.send("✅ Stok duyurusu kanala başarıyla gönderildi!", ephemeral=True)


class AdminServiceSelectForStock(discord.ui.Select):
    def __init__(self, action="add"):
        self.action = action
        services = db.get_services()
        options = []
        for s in services:
            count = db.get_stock_count(s["id"])
            cat = "⭐ VIP" if s.get("category") == "vip" else "🎁 FREE"
            is_unlimited = s.get("id") in ["steam_free", "gemini_pro", "mc_vip", "tonguc_vip", "tod_tv_vip", "prime_video_vip"] or s.get("is_unlimited", False)
            is_ticket = s.get("requires_ticket", False)
            if is_ticket:
                count_str = "🎫 Ticket Manuel"
            elif is_unlimited:
                count_str = "∞ Sınırsız"
            else:
                count_str = f"{count} adet"

            options.append(discord.SelectOption(
                label=f"{s['name']}",
                value=s["id"],
                description=f"[{cat}] Mevcut Stok: {count_str}",
                emoji=s.get("emoji", "📦")
            ))
        super().__init__(
            placeholder="👇 İşlem yapmak istediğiniz servisi seçin...",
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        service_id = self.values[0]
        service = db.get_service(service_id)
        if not service:
            await interaction.response.send_message("❌ Servis bulunamadı!", ephemeral=True)
            return

        if self.action == "add":
            modal = AddStockModal(service_id=service_id, service_name=service["name"])
            await interaction.response.send_modal(modal)
        elif self.action == "clear":
            await interaction.response.defer(ephemeral=True)
            removed = db.clear_stock(service_id)
            await interaction.followup.send(
                f"🗑️ **{service['name']}** servisinin **{removed}** adet stoğu sıfırlandı!",
                ephemeral=True
            )


class AdminResetUserSelect(discord.ui.UserSelect):
    def __init__(self):
        super().__init__(placeholder="👇 Günlük hakkı sıfırlanacak üyeyi seçin...", min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        target_user = self.values[0]
        db.reset_user_cooldown(target_user.id)
        embed = discord.Embed(
            title="🔄 Günlük Hak Sıfırlandı",
            description=f"**{target_user.mention}** adlı kullanıcının stok bekleme süresi ve günlük limitleri sıfırlanmıştır!",
            color=discord.Color.green()
        )
        await interaction.followup.send(embed=embed, ephemeral=True)


class AdminVIPUserSelect(discord.ui.UserSelect):
    def __init__(self):
        super().__init__(placeholder="👇 Süresiz VIP verilecek veya kaldırılacak üyeyi seçin...", min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        target_user = self.values[0]
        is_current_vip = db.is_user_vip_db(target_user.id)
        new_status = not is_current_vip
        db.set_user_vip(target_user.id, new_status, duration_hours=0)

        status_txt = "⭐ **Süresiz VIP Verildi**" if new_status else "❌ **VIP Kaldırıldı**"
        embed = discord.Embed(
            title="👑 VIP Üyelik Güncellendi",
            description=f"Kullanıcı: {target_user.mention}\nYeni Durum: {status_txt}",
            color=discord.Color.gold() if new_status else discord.Color.red()
        )
        await interaction.followup.send(embed=embed, ephemeral=True)


class Admin1DayVIPUserSelect(discord.ui.UserSelect):
    def __init__(self):
        super().__init__(placeholder="🏆 Kazanan Üyeyi Seç (24 Saatlik VIP Ver)...", min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        target_user = self.values[0]
        db.set_user_vip(target_user.id, True, duration_hours=24)

        embed = discord.Embed(
            title="🏆 1 GÜNLÜK (24 SAAT) VIP VERİLDİ!",
            description=(
                f"🎉 Tebrikler {target_user.mention}!\n\n"
                f"Hesabınıza **24 Saatlik VIP Üyelik** tanımlanmıştır! "
                f"VIP servislerden hemen stok alabilirsiniz. 🚀"
            ),
            color=discord.Color.gold(),
            timestamp=discord.utils.utcnow()
        )
        embed.set_footer(text="LeaksTr Admin Event Winner Award • 24 Saat Süreli VIP")
        await interaction.followup.send(embed=embed, ephemeral=False)


class AdminControlPanelContainerView(discord.ui.View):
    def __init__(self, content_type: str):
        super().__init__(timeout=120)
        if content_type == "add_stock":
            self.add_item(AdminServiceSelectForStock(action="add"))
        elif content_type == "clear_stock":
            self.add_item(AdminServiceSelectForStock(action="clear"))
        elif content_type == "reset_user":
            self.add_item(AdminResetUserSelect())
        elif content_type == "manage_vip":
            self.add_item(AdminVIPUserSelect())
        elif content_type == "give_1day_vip":
            self.add_item(Admin1DayVIPUserSelect())


class AdminPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=180)

    @discord.ui.button(label="📦 Stok Yükle", style=discord.ButtonStyle.primary, emoji="➕")
    async def add_stock_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = AdminControlPanelContainerView("add_stock")
        await interaction.response.send_message("👇 Stok eklemek istediğiniz servisi seçin:", view=view, ephemeral=True)

    @discord.ui.button(label="👑 Süresiz VIP Yönetimi", style=discord.ButtonStyle.success, emoji="⭐")
    async def vip_manage_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = AdminControlPanelContainerView("manage_vip")
        await interaction.response.send_message("👇 VIP durumunu değiştirmek istediğiniz üyeyi seçin:", view=view, ephemeral=True)

    @discord.ui.button(label="🏆 Kazanana 1 Günlük VIP Ver", style=discord.ButtonStyle.secondary, emoji="🏆")
    async def give_1day_vip_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = AdminControlPanelContainerView("give_1day_vip")
        await interaction.response.send_message("👇 Etkinlik/Çekiliş kazanan üyeyi seçin:", view=view, ephemeral=True)

    @discord.ui.button(label="📊 İstatistikler", style=discord.ButtonStyle.primary, emoji="📊")
    async def stats_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        stats = db.get_admin_stats()
        uptime_str = format_seconds(time.time() - BOT_START_TIME)

        embed = discord.Embed(
            title="📊 LeaksTr Yöntici İstatistik & Rapor Paneli",
            description="Sunucunun ve generator botunun anlık detaylı verileri aşağıda raporlanmıştır:",
            color=discord.Color.gold(),
            timestamp=discord.utils.utcnow()
        )
        embed.add_field(name="📦 Toplam Servis Sayısı", value=f"**{stats['total_services']}** aktif servis", inline=True)
        embed.add_field(name="📥 Bekleyen Stok Sayısı", value=f"**{stats['total_current_stock']:,}** adet", inline=True)
        embed.add_field(name="🚀 Toplam Teslim Edilen Stok", value=f"**{stats['total_claims_all_time']:,}** adet", inline=True)

        embed.add_field(name="🪙 Dolaşımdaki Coin", value=f"**{stats['total_coins_in_circulation']:,} Coin**", inline=True)
        embed.add_field(name="👥 Kayıtlı Üye Sayısı", value=f"**{stats['total_registered_users']}** üye", inline=True)
        embed.add_field(name="⭐ Aktif VIP Üye Sayısı", value=f"**{stats['total_vip_users']}** üye", inline=True)

        embed.add_field(name="🗣️ Chat Şartı Sağlayan Üye", value=f"**{stats['chatted_users_count']}** üye", inline=True)
        embed.add_field(name="🔗 Toplam Yapılan Davet", value=f"**{stats['total_invites']}** davet", inline=True)
        embed.add_field(name="🔥 En Çok Alınan Servis", value=f"**{stats['most_claimed_service']}**", inline=True)

        embed.add_field(name="⏱️ Bot Çalışma Süresi (Uptime)", value=f"**{uptime_str}**", inline=True)
        embed.add_field(name="⚡ Anlık API Gecikmesi (Ping)", value=f"**{round(bot.latency * 1000)} ms**", inline=True)

        embed.set_footer(text="LeaksTr Admin Analytics System • Canlı Veri")
        await interaction.followup.send(embed=embed, ephemeral=True)

    @discord.ui.button(label="🔄 Hak Sıfırla", style=discord.ButtonStyle.secondary, emoji="⚡")
    async def reset_limit_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = AdminControlPanelContainerView("reset_user")
        await interaction.response.send_message("👇 Bekleme süresini sıfırlamak istediğiniz üyeyi seçin:", view=view, ephemeral=True)

    @discord.ui.button(label="📢 Stok Duyurusu", style=discord.ButtonStyle.primary, emoji="🚀")
    async def announce_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = RestockAnnouncementModal()
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="🗑️ Stok Sıfırla", style=discord.ButtonStyle.danger, emoji="❌")
    async def clear_stock_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = AdminControlPanelContainerView("clear_stock")
        await interaction.response.send_message("⚠️ Stoklarını temizlemek istediğiniz servisi seçin:", view=view, ephemeral=True)


# --- GENERAL USER DROPDOWNS & VIEWS ---

class ServiceSelect(discord.ui.Select):
    def __init__(self, category: str, is_vip: bool):
        self.category = category
        self.is_vip = is_vip
        
        services = db.get_services(category=category)
        options = []

        if not services:
            options.append(discord.SelectOption(
                label="Bu kategoride servis bulunamadı",
                value="none",
                description="Lütfen daha sonra tekrar kontrol edin.",
                emoji="❌"
            ))
        else:
            for s in services:
                count = db.get_stock_count(s["id"])
                emoji = s.get("emoji", "🎁")
                is_unlimited = s.get("id") in ["steam_free", "gemini_pro", "mc_vip", "tonguc_vip", "tod_tv_vip", "prime_video_vip"] or s.get("is_unlimited", False)
                is_ticket = s.get("requires_ticket", False) or s.get("id") in ["mailchecker_tool", "nitro_promo", "spotify_premium_vip"]
                
                if is_ticket:
                    count_str = "🎫 Özel Ticket Açılır"
                elif is_unlimited:
                    count_str = "Sınırsız (Random)"
                else:
                    count_str = f"Stok: {count} adet"

                desc = f"{count_str} | {s.get('description', '')[:30]}"
                options.append(discord.SelectOption(
                    label=s["name"][:100],
                    value=s["id"],
                    description=desc[:100],
                    emoji=emoji
                ))

        super().__init__(
            placeholder="👇 Lütfen almak istediğiniz servisi seçin...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id=f"select_service_{category}"
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        service_id = self.values[0]
        if service_id == "none":
            await interaction.followup.send("❌ Bu kategoride henüz aktif servis bulunmuyor.", ephemeral=True)
            return

        service = db.get_service(service_id)
        if not service:
            await interaction.followup.send("❌ Servis bulunamadı!", ephemeral=True)
            return

        user = interaction.user
        member = interaction.guild.get_member(user.id) if interaction.guild else None
        
        # 1. CHECK ANTI-ALT (Account Age < 7 Days)
        if member:
            passed_alt, age_days = check_anti_alt(member)
            if not passed_alt:
                config = db.get_config()
                min_days = config.get("min_account_age_days", 7)
                embed = discord.Embed(
                    title="🛡️ Anti-Alt (Yan Hesap) Koruması Devrede!",
                    description=(
                        f"Stok güvenliği nedeniyle Discord hesabınızın en az **{min_days} günlük** "
                        f"olması gerekmektedir.\n\n"
                        f"📌 **Mevcut Hesap Yaşınız:** `{age_days} gün`"
                    ),
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return

        # 2. CHECK CUSTOM STATUS FOR "LeaksTr"
        if member and not check_user_custom_status(member):
            config = db.get_config()
            req_text = config.get("required_status", "LeaksTr")
            embed = discord.Embed(
                title="❌ Özel Durum Şartı Sağlanmadı!",
                description=(
                    f"Stok alabilmek için Discord **Özel Durumunuza (Custom Status)** "
                    f"**`{req_text}`** eklemeniz gerekmektedir!\n\n"
                    f"📌 **Örnek Kullanım:**\n"
                    f"• `.gg/{req_text}` veya `{req_text} Best Generator`\n\n"
                    f"*(Durumunuzu güncelledikten sonra hemen tekrar deneyebilirsiniz)*"
                ),
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        # 3. CHECK CHAT ACTIVITY (Must have sent at least 1 message)
        if member and not check_user_chat_activity(member):
            embed = discord.Embed(
                title="💬 Chat Aktiflik Şartı Sağlanmadı!",
                description=(
                    "Stok veya ödül alabilmek için sunucu kanallarına **en az 1 adet mesaj** göndermiş olmanız gerekmektedir!\n\n"
                    "📌 **Ne Yapmalıyım?**\n"
                    "• Sunucu sohbet kanalına gidin ve en az 1 mesaj yazın (Selam vb.).\n"
                    "• Mesajınızı attıktan sonra hemen gelip stok alabilirsiniz!"
                ),
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        # 4. CHECK VIP & BOOSTER TIER
        user_is_booster = is_booster_user(member) if member else False
        user_is_vip = is_vip_user(member) if member else False

        if service.get("category") == "vip" and not user_is_vip:
            embed = discord.Embed(
                title="🔒 VIP Servis Erişimi Engellendi",
                description="Bu servis **VIP ve Server Booster üyeler** içindir!\nVIP üyelik almak veya sunucuya Nitro Boost basmak için yöneticilerle iletişime geçin.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        # 5. CHECK COOLDOWN
        can_claim, remaining_sec, claims_count, daily_limit = db.check_user_cooldown(
            user.id, is_vip=user_is_vip, is_booster=user_is_booster
        )

        if not can_claim:
            time_str = format_seconds(remaining_sec)
            unlock_timestamp = int(time.time() + remaining_sec)
            embed = discord.Embed(
                title="⏳ Günlük Sınıra Ulaşıldı!",
                description=(
                    f"Günlük stok alma sınırına ulaştınız! (**{claims_count}/{daily_limit}**)\n\n"
                    f"⏱️ **Yeniden alma hakkı:** <t:{unlock_timestamp}:R> ({time_str} sonra)"
                ),
                color=discord.Color.orange()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        # 6. SPECIAL TICKET FLOW FOR MailChecker, Nitro Promo & Spotify Premium
        is_ticket_service = service.get("requires_ticket") or (service_id in ["mailchecker_tool", "nitro_promo", "spotify_premium_vip"])
        if is_ticket_service:
            guild = interaction.guild
            if not guild:
                await interaction.followup.send("❌ Ticket açma işlemi sunucuda gerçekleştirilmelidir.", ephemeral=True)
                return

            if service_id == "nitro_promo":
                prefix_str = "nitro-promo"
            elif service_id == "spotify_premium_vip":
                prefix_str = "spotify-premium"
            else:
                prefix_str = "mailchecker"

            channel_name = f"📩-{prefix_str}-{user.name[:10]}".lower().replace(" ", "-")
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, attach_files=True),
                guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_channels=True)
            }

            cfg = db.get_config()
            admin_role_id = cfg.get("admin_role_id", 0)
            if admin_role_id:
                admin_role = guild.get_role(int(admin_role_id))
                if admin_role:
                    overwrites[admin_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True)

            try:
                ticket_channel = await guild.create_text_channel(
                    name=channel_name,
                    overwrites=overwrites,
                    topic=f"{service['name']} Talebi - {user.name} ({user.id})"
                )

                ticket_embed = discord.Embed(
                    title=f"🛠️ {service['name']} Talebi Alındı!",
                    description=(
                        f"Merhaba {user.mention}!\n\n"
                        f"📌 **{service['name']}** talebiniz başarıyla oluşturuldu.\n"
                        f"Yetkililerimiz (Efe / Admin) en kısa sürede **size özel canlı URL / Kodu** "
                        f"bu kanala manuel olarak iletecektir.\n\n"
                        f"⏱️ Lütfen bekleyin ve kanal bildirimlerinizi açık tutun!"
                    ),
                    color=discord.Color.gold(),
                    timestamp=discord.utils.utcnow()
                )
                ticket_embed.set_footer(text="İşleminiz bittiğinde aşağıdaki '🔒 Ticket'ı Kapat' butonuna basabilirsiniz.")
                
                await ticket_channel.send(content=f"🔔 {user.mention} @here", embed=ticket_embed, view=CloseTicketView())

                db.record_claim(user.id, service_id, f"TICKET: #{ticket_channel.name}", is_vip=user_is_vip)

                success_embed = discord.Embed(
                    title="🎫 Ticket Kanalınız Açıldı!",
                    description=f"**{service['name']}** talebiniz için özel kanal oluşturuldu:\n👉 {ticket_channel.mention}\n\nLütfen kanala giderek yetkilimizin size özel kodunuzu/linkinizi vermesini bekleyin.",
                    color=discord.Color.green()
                )
                await interaction.followup.send(embed=success_embed, ephemeral=True)

                if interaction.guild:
                    await log_claim(interaction.guild, user, service, f"TICKET: #{ticket_channel.name}", is_vip=user_is_vip)
                return

            except Exception as e:
                await interaction.followup.send(f"❌ Ticket kanalı oluşturulurken hata oluştu: {e}", ephemeral=True)
                return

        # 7. STANDARD STOCK CLAIM & RETRIEVAL
        is_unlimited = (service_id in ["steam_free", "gemini_pro", "mc_vip", "tonguc_vip", "tod_tv_vip", "prime_video_vip"]) or service.get("is_unlimited", False)
        stock_count = db.get_stock_count(service_id)

        if stock_count <= 0:
            embed = discord.Embed(
                title="❌ Stok Tükenmiş!",
                description=f"**{service['name']}** servisinde şu anda hesap bulunmamaktadır.\nYetkililer en kısa sürede stok yükleyecektir!",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        account_data = db.get_stock_account(service_id)
        if not account_data:
            await interaction.followup.send("❌ Stok çekilirken bir hata oluştu, lütfen tekrar deneyin.", ephemeral=True)
            return

        # RECORD CLAIM
        db.record_claim(user.id, service_id, account_data, is_vip=user_is_vip)

        dm_embed = discord.Embed(
            title=f"{service.get('emoji', '🎁')} {service['name']} Hesabınız Hazır!",
            description="Hesap bilgileriniz / yayın linkiniz aşağıda verilmiştir. Güle güle kullanın!",
            color=discord.Color.gold() if service.get("category") == "vip" else discord.Color.green(),
            timestamp=discord.utils.utcnow()
        )
        dm_embed.add_field(
            name="🔑 Hesap / Link Bilgileri",
            value=f"```\n{account_data}\n```",
            inline=False
        )
        
        stk_rem_txt = "∞ Sınırsız (Random)" if is_unlimited else f"{db.get_stock_count(service_id)} adet"
        dm_embed.add_field(
            name="ℹ️ Bilgilendirme",
            value=f"Günlük Kullanılan Hak: **{claims_count + 1}/{daily_limit}**\nServiste Kalan Stok: **{stk_rem_txt}**",
            inline=False
        )
        dm_embed.add_field(
            name="⚠️ Hatalı Stok mu Geldi?",
            value="Hesabınız çalışmıyorsa sunucumuzdaki paneldan **`⚠️ Hatalı Stok Bildir`** butonuna tıklayarak hataya dair **ekran görüntüsü (görsel)** iletebilirsiniz!",
            inline=False
        )
        dm_embed.add_field(
            name="⚖️ Yasal Uyarı & Sorumluluk Reddi",
            value="Temin edilen hesap ve yayın linklerinin kullanım sorumluluğu tamamen kullanıcıya aittir. LeaksTr hiçbir yasal sorumluluk kabul etmez.",
            inline=False
        )
        dm_embed.set_footer(text="LeaksTr Generator System • 7/24 Otomatik Hizmet")

        dm_sent = False
        try:
            await user.send(embed=dm_embed)
            dm_sent = True
        except Exception:
            dm_sent = False

        if dm_sent:
            success_embed = discord.Embed(
                title="✅ Stok Teslim Edildi!",
                description=f"**{service['name']}** hesabınız **DM (Direkt Mesaj)** kutunuza başarıyla gönderildi!\nLütfen DM kutunuzu kontrol edin.",
                color=discord.Color.green()
            )
            await interaction.followup.send(embed=success_embed, ephemeral=True)
        else:
            fallback_embed = discord.Embed(
                title="⚠️ DM Kutunuz Kapalı!",
                description=f"DM kutunuz kapalı olduğu için mesaj gönderilemedi. Hesabınız aşağıdadır (Sadece siz görüyorsunuz):\n\n**🔑 Hesap / Link Bilgisi:**\n```\n{account_data}\n```\n\n⚠️ *Hesabınız çalışmıyorsa paneldan '⚠️ Hatalı Stok Bildir' butonuna basarak ekran görüntüsü iletin.*",
                color=discord.Color.yellow()
            )
            fallback_embed.set_footer(text="Lütfen gelecekteki alımlar için sunucu DM'lerinizi açın!")
            await interaction.followup.send(embed=fallback_embed, ephemeral=True)

        if interaction.guild:
            await log_claim(interaction.guild, user, service, account_data, is_vip=user_is_vip)


class CategorySelectView(discord.ui.View):
    def __init__(self, category: str, is_vip: bool):
        super().__init__(timeout=120)
        self.add_item(ServiceSelect(category, is_vip))


class MainPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="FREE Servisler",
        style=discord.ButtonStyle.primary,
        emoji="🎁",
        custom_id="btn_free_services"
    )
    async def free_services_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        view = CategorySelectView(category="free", is_vip=False)
        embed = discord.Embed(
            title="🎁 Free (Ücretsiz) Servisler",
            description="Aşağıdaki açılır menüden almak istediğiniz ücretsiz servisi seçin:",
            color=discord.Color.blue()
        )
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)

    @discord.ui.button(
        label="VIP Servisler",
        style=discord.ButtonStyle.success,
        emoji="⭐",
        custom_id="btn_vip_services"
    )
    async def vip_services_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        member = interaction.guild.get_member(interaction.user.id) if interaction.guild else None
        user_is_vip = is_vip_user(member) if member else False

        if not user_is_vip:
            embed = discord.Embed(
                title="🔒 VIP Servis Erişimi Engellendi",
                description="Bu servis alanı **sadece VIP ve Server Booster üyeler** içindir!\nVIP üyelik almak veya sunucuya Nitro Boost basmak için yöneticilerle iletişime geçin.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        view = CategorySelectView(category="vip", is_vip=True)
        embed = discord.Embed(
            title="⭐ VIP (Ayrıcalıklı) Servisler",
            description="Aşağıdaki açılır menüden almak istediğiniz VIP servisi seçin:",
            color=discord.Color.gold()
        )
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)

    @discord.ui.button(
        label="Coin Market",
        style=discord.ButtonStyle.success,
        emoji="🪙",
        custom_id="btn_coin_market"
    )
    async def coin_market_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        u_data = db.get_user_data(interaction.user.id)
        coins = u_data.get("coins", 0)

        embed = discord.Embed(
            title="🪙 LeaksTr Coin Mağazası & Bakiyem",
            description=(
                f"Hoş geldiniz! Hesabınızda **{coins} Coin** bulunmaktadır.\n\n"
                f"💳 **Hesap.com.tr İle Coin Satın Alma:**\n"
                f"• **20 TL = 100 Coin**\n"
                f"• [👉 Hesap.com.tr Mağazamız İçin Tıklayın](https://hesap.com.tr)\n\n"
                f"🛒 **Coin Harcama Fiyatları:**\n"
                f"• **🎧 100 Coin = Spotify Premium Bireysel (Ticket)**\n"
                f"• **🚀 100 Coin = Discord Nitro Promo (Ticket)**\n"
                f"• **🤖 50 Coin = Google Gemini Pro (Sınırsız Hesabı)**\n"
                f"• **⭐ 20 Coin = 24 Saatlik VIP Üyelik**\n"
                f"• **🎁 20 Coin = +1 Ekstra Stok Hakkı (Sıfırlama)**\n\n"
                f"*(Aşağıdaki butonları kullanarak bakiyenizle anında satın alabilirsiniz)*"
            ),
            color=discord.Color.gold(),
            timestamp=discord.utils.utcnow()
        )
        embed.set_footer(text="LeaksTr Coin Sistemi • Otomatik Anında Teslimat")
        view = CoinMarketView()
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)

    @discord.ui.button(
        label="Günlük Şans Çarkı",
        style=discord.ButtonStyle.primary,
        emoji="🎰",
        custom_id="btn_daily_wheel"
    )
    async def daily_wheel_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        user = interaction.user
        
        can_spin, remaining_sec = db.check_user_wheel_spin(user.id)
        if not can_spin:
            unlock_timestamp = int(time.time() + remaining_sec)
            embed = discord.Embed(
                title="⏳ Şans Çarkı Bekleme Süresi!",
                description=f"Günlük Şans Çarkını çevirdiniz!\n\n⏱️ **Yeniden Çevirme Hakkı:** <t:{unlock_timestamp}:R> ({format_seconds(remaining_sec)})",
                color=discord.Color.orange()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        # RECORD SPIN
        db.record_wheel_spin(user.id)

        # ROLL OUTCOME
        outcomes = ["claim", "vip", "coin", "steam", "key", "miss"]
        weights = [30, 20, 15, 15, 10, 10]
        won_type = random.choices(outcomes, weights=weights, k=1)[0]

        if won_type == "claim":
            db.reset_user_cooldown(user.id)
            title = "🎉 TEBRİKLER! +1 EKSTRA STOK HAKKI KAZANDINIZ!"
            desc = "Günlük bekleme süreniz sıfırlandı! Hemen dilediğiniz bir servisten stok alabilirsiniz. 🎁"
            color = discord.Color.green()
        elif won_type == "vip":
            db.set_user_vip(user.id, True, duration_hours=24)
            title = "⭐ TEBRİKLER! 24 SAATLİK VIP ÜYELİK KAZANDINIZ!"
            desc = "24 saat boyunca tüm VIP servislerden stok alma hakkınız aktif edildi! 🚀"
            color = discord.Color.gold()
        elif won_type == "coin":
            tot = db.add_user_coins(user.id, 50)
            title = "🪙 TEBRİKLER! 50 COIN KAZANDINIZ!"
            desc = f"Hesabınıza 50 Coin tanımlandı! (Güncel Bakiyeniz: {tot} Coin) 💰"
            color = discord.Color.gold()
        elif won_type == "steam":
            acc = db.get_stock_account("steam_free")
            if acc:
                title = "🎮 TEBRİKLER! ANINDA STEAM OYUN HESABI KAZANDINIZ!"
                desc = f"Çarktan kazandığınız oyunlu Steam hesabı:\n```\n{acc}\n```"
            else:
                title = "🎮 TEBRİKLER! OYUNLU STEAM HAKKI KAZANDINIZ!"
                desc = "Steam stoklarımız yenilendiğinde hesabınız teslim edilecektir."
            color = discord.Color.purple()
        elif won_type == "key":
            keys = db.create_promo_keys("coin", "100", count=1)
            title = "🔑 TEBRİKLER! 100 COINLİK SÜRPRİZ PROMO KODU KAZANDINIZ!"
            desc = f"Kazandığınız Promo Kodu:\n`{keys[0]}`\n\nBu kodu `/kod-kullan {keys[0]}` yazarak 100 Coin bakiyenize dönüştürebilirsiniz!"
            color = discord.Color.teal()
        else:
            title = "❌ MAALESEF ŞANSINA KÜS!"
            desc = "Çark bu sefer boş geldi. Şansını yarın tekrar dene! 💪"
            color = discord.Color.red()

        wheel_embed = discord.Embed(
            title=f"🎰 {user.name} Şans Çarkını Çevirdi!",
            description=f"**{title}**\n\n{desc}",
            color=color,
            timestamp=discord.utils.utcnow()
        )
        wheel_embed.set_footer(text="LeaksTr Günlük Şans Çarkı • 24 Saatte 1 Çevirme Hakkı")
        await interaction.followup.send(embed=wheel_embed, ephemeral=True)

    @discord.ui.button(
        label="Hatalı Stok Bildir",
        style=discord.ButtonStyle.danger,
        emoji="⚠️",
        custom_id="btn_report_broken_stock"
    )
    async def report_broken_stock_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        user = interaction.user
        guild = interaction.guild

        if not guild:
            await interaction.followup.send("❌ Bu işlem sadece sunucu içerisinde gerçekleştirilebilir.", ephemeral=True)
            return

        channel_name = f"🚨-hatali-stok-{user.name[:10]}".lower().replace(" ", "-")
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, attach_files=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_channels=True)
        }

        cfg = db.get_config()
        admin_role_id = cfg.get("admin_role_id", 0)
        if admin_role_id:
            admin_role = guild.get_role(int(admin_role_id))
            if admin_role:
                overwrites[admin_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True)

        try:
            ticket_channel = await guild.create_text_channel(
                name=channel_name,
                overwrites=overwrites,
                topic=f"Hatalı Stok Bildirimi - {user.name} ({user.id})"
            )

            ticket_embed = discord.Embed(
                title="🚨 Hatalı Stok Bildirimi & Telafi Destek Kanalı",
                description=(
                    f"Merhaba {user.mention}!\n\n"
                    f"Aldığınız stokta veya hesapta bir sorun mu yaşadınız? Hiç endişelenmeyin!\n\n"
                    f"📸 **LÜTFEN HATAYA DAİR EKRAN GÖRÜNTÜSÜ / GÖRSEL İLETİN:**\n"
                    f"• Yaşadığınız hatayı net gösteren **ekran görüntüsünü (görseli)** bu kanala yükleyin.\n"
                    f"• Aldığınız servisi ve hesap bilgisini belirtin.\n\n"
                    f"Yetkililerimiz (Efe / Admin) ilettiğiniz **görseli inceleyip anında yeni çalışan stok veya telafi hakkı** verecektir!"
                ),
                color=discord.Color.red(),
                timestamp=discord.utils.utcnow()
            )
            ticket_embed.set_footer(text="Görselinizi ilettikten sonra yetkilimizin yanıtını bekleyin. İşlem bitince kapatabilirsiniz.")
            
            await ticket_channel.send(content=f"🔔 {user.mention} @here", embed=ticket_embed, view=CloseTicketView())

            success_embed = discord.Embed(
                title="🎫 Hatalı Stok Ticket Kanalınız Açıldı!",
                description=f"Telafi talebiniz için özel destek kanalı açıldı:\n👉 {ticket_channel.mention}\n\nLütfen kanala giderek **hataya dair ekran görüntüsünü (görseli)** iletin.",
                color=discord.Color.green()
            )
            await interaction.followup.send(embed=success_embed, ephemeral=True)

        except Exception as e:
            await interaction.followup.send(f"❌ Ticket kanalı açılırken hata oluştu: {e}", ephemeral=True)

    @discord.ui.button(
        label="Stok Durumu",
        style=discord.ButtonStyle.secondary,
        emoji="📊",
        custom_id="btn_stock_status"
    )
    async def stock_status_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        services = db.get_services()
        
        free_services = [s for s in services if s.get("category") == "free"]
        vip_services = [s for s in services if s.get("category") == "vip"]

        embed = discord.Embed(
            title="📊 Anlık Stok Durumu",
            description="Tüm servislerimizin güncel stok sayıları aşağıda listelenmiştir:",
            color=discord.Color.purple(),
            timestamp=discord.utils.utcnow()
        )

        free_text = ""
        for s in free_services:
            count = db.get_stock_count(s["id"])
            is_unlimited = s.get("id") in ["steam_free", "gemini_pro", "mc_vip", "tonguc_vip", "tod_tv_vip", "prime_video_vip"] or s.get("is_unlimited", False)
            is_ticket = s.get("requires_ticket", False) or s.get("id") in ["mailchecker_tool", "nitro_promo", "spotify_premium_vip"]
            
            status = "🟢"
            if is_ticket:
                count_txt = "🎫 Özel Ticket"
            elif is_unlimited:
                count_txt = "∞ Sınırsız"
            else:
                status = "🟢" if count > 0 else "🔴"
                count_txt = f"{count} adet"

            free_text += f"{status} {s.get('emoji', '🎁')} **{s['name']}**: `{count_txt}`\n"

        vip_text = ""
        for s in vip_services:
            count = db.get_stock_count(s["id"])
            is_unlimited = s.get("id") in ["gemini_pro", "mc_vip", "tonguc_vip", "tod_tv_vip", "prime_video_vip"] or s.get("is_unlimited", False)
            is_ticket = s.get("requires_ticket", False) or s.get("id") in ["nitro_promo", "spotify_premium_vip"]
            status = "🟢"
            if is_ticket:
                count_txt = "🎫 Özel Ticket"
            elif is_unlimited:
                count_txt = "∞ Sınırsız"
            else:
                status = "🟢" if count > 0 else "🔴"
                count_txt = f"{count} adet"

            vip_text += f"{status} {s.get('emoji', '⭐')} **{s['name']}**: `{count_txt}`\n"

        embed.add_field(name="🎁 FREE Servis Stokları", value=free_text or "Servis bulunmuyor.", inline=False)
        embed.add_field(name="⭐ VIP Servis Stokları", value=vip_text or "Servis bulunmuyor.", inline=False)
        embed.set_footer(text="Stoklar otomatik olarak güncellenir.")

        await interaction.followup.send(embed=embed, ephemeral=True)

    @discord.ui.button(
        label="Profilim / Haklarım",
        style=discord.ButtonStyle.secondary,
        emoji="👤",
        custom_id="btn_user_profile"
    )
    async def user_profile_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        user = interaction.user
        member = interaction.guild.get_member(user.id) if interaction.guild else None
        
        user_is_booster = is_booster_user(member) if member else False
        user_is_vip = is_vip_user(member) if member else False

        user_data = db.get_user_data(user.id)
        can_claim, remaining_sec, claims_count, daily_limit = db.check_user_cooldown(
            user.id, is_vip=user_is_vip, is_booster=user_is_booster
        )

        if user_is_booster:
            status_str = "🚀 Server Booster (3 Hak)"
        elif user_is_vip:
            status_str = f"⭐ VIP Üye ({daily_limit} Hak)"
        else:
            status_str = f"🎁 Normal Üye ({daily_limit} Hak)"

        has_status = check_user_custom_status(member) if member else True
        custom_st_txt = "✅ Sağlandı (LeaksTr)" if has_status else "❌ Eksik (LeaksTr ekleyin)"

        has_chatted = check_user_chat_activity(member) if member else True
        chat_st_txt = "✅ Sağlandı (Aktif)" if has_chatted else "❌ Eksik (Mesaj atın)"

        passed_alt, age_days = check_anti_alt(member) if member else (True, 999)
        alt_txt = f"✅ Onaylı ({age_days} gün)" if passed_alt else f"❌ Çok Yeni ({age_days} gün)"

        embed = discord.Embed(
            title=f"👤 {user.name} - Kullanıcı Profili",
            color=discord.Color.magenta() if user_is_booster else (discord.Color.gold() if user_is_vip else discord.Color.blue()),
            timestamp=discord.utils.utcnow()
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.add_field(name="👑 Üyelik Statüsü", value=f"**{status_str}**", inline=True)
        embed.add_field(name="🪙 Coin Bakiyesi", value=f"**{user_data.get('coins', 0)} Coin**", inline=True)
        embed.add_field(name="💬 Özel Durum Şartı", value=f"**{custom_st_txt}**", inline=True)
        embed.add_field(name="🗣️ Chat Mesaj Şartı", value=f"**{chat_st_txt}**", inline=True)
        embed.add_field(name="🛡️ Anti-Alt Durumu", value=f"**{alt_txt}**", inline=True)
        embed.add_field(name="👥 Davet Sayısı", value=f"**{user_data.get('invites', 0)}** davet", inline=True)
        embed.add_field(name="📦 Toplam Alınan Stok", value=f"**{user_data.get('total_claims', 0)}** adet", inline=True)
        embed.add_field(name="📊 Günlük Kullanım", value=f"**{claims_count} / {daily_limit}** hak kullanıldı", inline=False)

        if can_claim:
            embed.add_field(name="✅ Durum", value=f"Şu an **{daily_limit - claims_count} adet** stok alma hakkınız bulunmaktadır!", inline=False)
        else:
            unlock_timestamp = int(time.time() + remaining_sec)
            embed.add_field(
                name="⏳ Sıfırlanma Zamanı",
                value=f"Kalan Süre: <t:{unlock_timestamp}:R> ({format_seconds(remaining_sec)})",
                inline=False
            )

        await interaction.followup.send(embed=embed, ephemeral=True)

    @discord.ui.button(
        label="Sorumluluk Reddi",
        style=discord.ButtonStyle.secondary,
        emoji="📜",
        custom_id="btn_disclaimer"
    )
    async def disclaimer_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        embed = discord.Embed(
            title="秤 LEAKSTR YASAL UYARI & SORUMLULUK REDDİ BEYANI",
            description=(
                "**1. Taraf ve Sorumluluk Sınırı:**\n"
                "LeaksTr Generator, bot yöneticileri ve sunucu sahipleri; bu sistem üzerinden "
                "dağıtılan, teslim edilen veya erişimi sağlanan hiçbir hesap, dijital materyal, "
                "yayın linki (IPTV, M3U8, Embed) veya içeriğin sağlayıcısı veya mülkiyet sahibi değildir.\n\n"
                "**2. Kullanıcı Sorumluluğu:**\n"
                "Sistemden stok alan, link kullanan veya hesap temin eden her kullanıcı; temin ettiği veriyi "
                "kendi şahsi sorumluluğunda ve riskinde kullanmayı kabul etmiş sayılır. Doğabilecek her türlü "
                "hukuki, mali, idari veya cezai sorumluluk **münhasıran kullanıcıya aittir**.\n\n"
                "**3. Telif Hakkı ve Bildirim:**\n"
                "Tüm içerikler üçüncü taraf açık kaynaklardan temin edilmektedir. Herhangi bir telif ihlali "
                "iddiasında ilgili hak sahipleri yöneticilerimizle iletişime geçerek içeriğin kaldırılmasını talep edebilir."
            ),
            color=discord.Color.red(),
            timestamp=discord.utils.utcnow()
        )
        embed.set_footer(text="LeaksTr Generator System • Yasal Şartlar & Kullanım Koşulları")
        await interaction.followup.send(embed=embed, ephemeral=True)

    @discord.ui.button(
        label="🏆 Liderlik Tablosu",
        style=discord.ButtonStyle.secondary,
        emoji="🏆",
        custom_id="btn_leaderboard"
    )
    async def leaderboard_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        leaderboard = db.get_leaderboard(limit=10)

        embed = discord.Embed(
            title="🏆 LeaksTr En Aktif Üyeler Liderlik Tablosu",
            description="En çok stok alan ve sunucuyu büyüten en aktif üyelerimiz:",
            color=discord.Color.gold(),
            timestamp=discord.utils.utcnow()
        )

        medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
        rank_text = ""
        for idx, entry in enumerate(leaderboard):
            medal = medals[idx] if idx < len(medals) else "🏅"
            u_id = entry["user_id"]
            claims = entry["claims"]
            invites = entry["invites"]
            coins = entry.get("coins", 0)
            vip_mark = "⭐" if entry["is_vip"] else ""
            rank_text += f"{medal} <@{u_id}> {vip_mark} • **{claims} Stok** | **{coins} Coin** | **{invites} Davet**\n"

        embed.add_field(name="Top 10 Üye", value=rank_text or "Henüz veri yok.", inline=False)
        await interaction.followup.send(embed=embed, ephemeral=True)

    @discord.ui.button(
        label="Admin Paneli",
        style=discord.ButtonStyle.danger,
        emoji="🛠️",
        custom_id="btn_admin_panel"
    )
    async def admin_panel_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        member = interaction.guild.get_member(interaction.user.id) if interaction.guild else None
        if not member or not is_admin_user(member):
            await interaction.response.send_message("❌ **Erişim Engellendi!** Bu panel sadece Yöneticilere özeldir.", ephemeral=True)
            return

        embed = discord.Embed(
            title="🛠️ Yönetici Kontrol Merkezi",
            description=(
                "Hoş geldiniz Yönetici! Aşağıdaki butonları kullanarak doğrudan panel üzerinden "
                "stok yükleyebilir, kullanıcı haklarını sıfırlayabilir veya VIP üyelik verebilirsiniz."
            ),
            color=discord.Color.red()
        )
        view = AdminPanelView()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


async def perform_sync_cleanly(guild_obj=None):
    raw_commands = list(bot.tree.get_commands())
    bot.tree.clear_commands(guild=None)
    await bot.tree.sync(guild=None)

    for cmd in raw_commands:
        bot.tree.add_command(cmd)

    if guild_obj:
        bot.tree.copy_global_to(guild=guild_obj)
        synced = await bot.tree.sync(guild=guild_obj)
        return len(synced)
    else:
        synced = await bot.tree.sync()
        return len(synced)


# --- BOT EVENTS & INVITE TRACKER & MESSAGE TRACKER ---
@bot.event
async def on_ready():
    print(f"Bot Giriş Yaptı: {bot.user.name} ({bot.user.id})")
    asyncio.create_task(start_web_server())

    bot.add_view(MainPanelView())
    bot.add_view(CloseTicketView())

    # Cache Invites
    for guild in bot.guilds:
        try:
            invites_cache[guild.id] = await guild.invites()
        except Exception:
            pass

    try:
        if GUILD_ID:
            guild_target = discord.Object(id=int(GUILD_ID))
            count = await perform_sync_cleanly(guild_obj=guild_target)
            print(f"⚡ Global komutlar silindi! {count} adet komut SADECE sunucuna ({GUILD_ID}) TEKİL olarak aktarıldı.")
        else:
            synced = await bot.tree.sync()
            print(f"Global komutlar senkronize edildi: {len(synced)} adet")
    except Exception as e:
        print(f"Komut Senkronizasyon Hatası: {e}")

    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="🪙 Coin Market, Free & VIP | !panel / !sync"
        )
    )

@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return
    if message.guild:
        db.record_user_message(message.author.id)
    await bot.process_commands(message)

@bot.event
async def on_member_join(member: discord.Member):
    guild = member.guild
    if guild.id not in invites_cache:
        return

    old_invites = invites_cache[guild.id]
    try:
        new_invites = await guild.invites()
        invites_cache[guild.id] = new_invites
        for inv in old_invites:
            for new_inv in new_invites:
                if inv.code == new_inv.code and new_inv.uses > inv.uses:
                    inviter = new_inv.inviter
                    if inviter and inviter.id != member.id:
                        total_inv = db.add_user_invite(inviter.id)
                        print(f"👥 [DAVET OK] {inviter.name} davetiyle {member.name} katıldı! (Toplam: {total_inv})")
                    break
    except Exception as e:
        print(f"Davet takip hatası: {e}")


# --- PREFIX COMMANDS ---

async def create_panel_embed_and_send(channel: discord.TextChannel, guild: discord.Guild):
    config = db.get_config()
    req_st = config.get("required_status", "LeaksTr")
    vip_limit = config.get("vip_daily_limit", 2)
    embed = discord.Embed(
        title="⚡ GENERATOR & STOK DAĞITIM PANELS ⚡",
        description=(
            "Hoş geldiniz! Aşağıdaki butonları kullanarak **Ücretsiz**, **VIP**, **Coin Market** veya **Şans Çarkından** "
            "hesap/kod/IPTV temin edebilirsiniz.\n\n"
            "📌 **Hızlı Kullanım Rehberi & Şartlar:**\n"
            f"• **💬 Şart 1 (Durum):** Profil durumunuzda **`{req_st}`** olmalıdır.\n"
            "• **🗣️ Şart 2 (Chat):** Sunucu kanallarından birine **en az 1 mesaj** yazmış olmalısınız.\n"
            "• **🎁 FREE Servisler:** Her 24 saatte 1 adet ücretsiz hesap alabilirsiniz.\n"
            f"• **⭐ VIP Servisler:** VIP üyeler için günlük **{vip_limit} adet** yüksek kaliteli stok alma hakkı!\n"
            "• **🪙 Coin Market:** 20 TL = 100 Coin! (Spotify Premium, Nitro Promo, Gemini Pro, VIP)\n"
            "• **⚠️ Hatalı Stok Bildir:** Hatalı hesaplar için ekran görüntülü anında telafi kanalı açılır!\n"
            "• **📺 IPTV Servisleri:** Canlı IPTV M3U8 ve Embed yayın linkleri.\n"
            "• **🚀 Nitro Booster Perks:** Nitro basanlara özel 3 adet günlük alma hakkı!\n"
            "• **🎰 Günlük Şans Çarkı:** Her gün 1 kere çevir, sürpriz VIP veya ekstra stok kazan!\n"
            "• **👥 Davet Sistemi:** 5 Arkadaşını davet et, OTOMATİK 1 Günlük VIP ol! (Günde 2 stok hakkı)\n"
            "• **🔍 MailChecker Tool:** Seçildiğinde özel Ticket kanalı açılır ve yetkili URL iletir.\n"
            "• **🎮 Steam Servisleri:** Sınırsız stok! Her alıma rastgele oyunlu hesap verilir.\n"
            "• **📜 Sorumluluk Reddi:** Tüm kullanım sorumluluğu alıcıya aittir.\n\n"
            "⚠️ *Hesaplar ve yayın linkleri doğrudan **DM (Direkt Mesaj)** kutunuza iletilmektedir.*"
        ),
        color=discord.Color.dark_theme()
    )
    embed.set_footer(text="LeaksTr Generator System • 7/24 Otomatik Hizmet")
    if guild and guild.icon:
        embed.set_thumbnail(url=guild.icon.url)

    view = MainPanelView()
    await channel.send(embed=embed, view=view)


@bot.command(name="panel", aliases=["kur", "start", "genpanel"])
@commands.has_permissions(administrator=True)
async def prefix_panel(ctx):
    try:
        await ctx.message.delete()
    except Exception:
        pass
    await create_panel_embed_and_send(ctx.channel, ctx.guild)


@bot.command(name="sync", aliases=["clearsync", "temizlesync", "temizle"])
@commands.has_permissions(administrator=True)
async def prefix_sync(ctx):
    msg = await ctx.send("⏳ Eski çift komutlar Discord API'sinden temizleniyor...")
    try:
        if GUILD_ID:
            guild_target = discord.Object(id=int(GUILD_ID))
            count = await perform_sync_cleanly(guild_obj=guild_target)
            await msg.edit(content=
                f"✅ **Eski çift komutlar tamamen temizlendi!**\n"
                f"`{ctx.guild.name}` sunucusunda **{count} adet TEKİL komut** aktif edildi!\n\n"
                f"💡 *Komut listeniz anında 1 adede düşmediyse Discord uygulamanızda **Ctrl + R** yaparak sayfayı yenileyin.*"
            )
        else:
            count = await perform_sync_cleanly()
            await msg.edit(content=f"✅ Global komutlar {count} adet olarak tekil güncellendi!")
    except Exception as e:
        await msg.edit(content=f"❌ Temizleme Hatası: {e}")


# --- SLASH COMMANDS ---

@bot.tree.command(name="vip-ver", description="🏆 Bir üyeye 1 günlük (veya istediğiniz süre) VIP tanımlar (Admin)")
@app_commands.default_permissions(administrator=True)
@app_commands.describe(kullanici="VIP verilecek üye", saat="Kaç saatlik VIP verilsin? (Varsayılan: 24 saat)")
async def vip_ver_command(interaction: discord.Interaction, kullanici: discord.User, saat: int = 24):
    if not is_admin_user(interaction.user):
        await interaction.response.send_message("❌ Bu komutu sadece Yöneticiler kullanabilir!", ephemeral=True)
        return

    db.set_user_vip(kullanici.id, True, duration_hours=saat)
    embed = discord.Embed(
        title="🏆 VIP ÜYELİK TANIMLANDI!",
        description=f"🎉 **{kullanici.mention}** adlı üyeye **{saat} Saatlik ({saat // 24} Günlük) VIP Üyelik** tanımlandı!",
        color=discord.Color.gold(),
        timestamp=discord.utils.utcnow()
    )
    embed.set_footer(text="LeaksTr VIP Award System")
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="istatistik", description="📊 Detaylı Admin İstatistik & Analiz Paneli (Admin)")
@app_commands.default_permissions(administrator=True)
async def istatistik_command(interaction: discord.Interaction):
    if not is_admin_user(interaction.user):
        await interaction.response.send_message("❌ Bu komutu sadece Yöneticiler kullanabilir!", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)
    stats = db.get_admin_stats()
    uptime_str = format_seconds(time.time() - BOT_START_TIME)

    embed = discord.Embed(
        title="📊 LeaksTr Yöntici İstatistik & Rapor Paneli",
        description="Sunucunun ve generator botunun anlık detaylı verileri aşağıda raporlanmıştır:",
        color=discord.Color.gold(),
        timestamp=discord.utils.utcnow()
    )
    embed.add_field(name="📦 Toplam Servis Sayısı", value=f"**{stats['total_services']}** aktif servis", inline=True)
    embed.add_field(name="📥 Bekleyen Stok Sayısı", value=f"**{stats['total_current_stock']:,}** adet", inline=True)
    embed.add_field(name="🚀 Toplam Teslim Edilen Stok", value=f"**{stats['total_claims_all_time']:,}** adet", inline=True)

    embed.add_field(name="🪙 Dolaşımdaki Coin", value=f"**{stats['total_coins_in_circulation']:,} Coin**", inline=True)
    embed.add_field(name="👥 Kayıtlı Üye Sayısı", value=f"**{stats['total_registered_users']}** üye", inline=True)
    embed.add_field(name="⭐ Aktif VIP Üye Sayısı", value=f"**{stats['total_vip_users']}** üye", inline=True)

    embed.add_field(name="🗣️ Chat Şartı Sağlayan Üye", value=f"**{stats['chatted_users_count']}** üye", inline=True)
    embed.add_field(name="🔗 Toplam Yapılan Davet", value=f"**{stats['total_invites']}** davet", inline=True)
    embed.add_field(name="🔥 En Çok Alınan Servis", value=f"**{stats['most_claimed_service']}**", inline=True)

    embed.add_field(name="⏱️ Bot Çalışma Süresi (Uptime)", value=f"**{uptime_str}**", inline=True)
    embed.add_field(name="⚡ Anlık API Gecikmesi (Ping)", value=f"**{round(bot.latency * 1000)} ms**", inline=True)

    embed.set_footer(text="LeaksTr Admin Analytics System • Canlı Veri")
    await interaction.followup.send(embed=embed, ephemeral=True)


@bot.tree.command(name="coin-ver", description="🪙 Bir kullanıcıya Coin bakiye yükler (Admin)")
@app_commands.default_permissions(administrator=True)
@app_commands.describe(kullanici="Coin verilecek üye", miktar="Eklenecek Coin miktarı (Örn: 100)")
async def coin_ver_command(interaction: discord.Interaction, kullanici: discord.User, miktar: int):
    if not is_admin_user(interaction.user):
        await interaction.response.send_message("❌ Bu komutu sadece Yöneticiler kullanabilir!", ephemeral=True)
        return

    new_bal = db.add_user_coins(kullanici.id, miktar)
    embed = discord.Embed(
        title="🪙 Coin Yüklendi!",
        description=f"**{kullanici.mention}** kullanıcısına **{miktar} Coin** eklendi!\nGüncel Bakiyesi: **{new_bal} Coin**",
        color=discord.Color.green()
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="coin-al", description="🪙 Bir kullanıcının bakiyesinden Coin düşer (Admin)")
@app_commands.default_permissions(administrator=True)
@app_commands.describe(kullanici="Coin düşülecek üye", miktar="Düşülecek Coin miktarı")
async def coin_al_command(interaction: discord.Interaction, kullanici: discord.User, miktar: int):
    if not is_admin_user(interaction.user):
        await interaction.response.send_message("❌ Bu komutu sadece Yöneticiler kullanabilir!", ephemeral=True)
        return

    db.remove_user_coins(kullanici.id, miktar)
    u_data = db.get_user_data(kullanici.id)
    embed = discord.Embed(
        title="🪙 Coin Düşüldü!",
        description=f"**{kullanici.mention}** kullanıcısının bakiyesinden **{miktar} Coin** düşüldü.\nGüncel Bakiyesi: **{u_data.get('coins', 0)} Coin**",
        color=discord.Color.orange()
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="kod-kullan", description="🎟️ Promo kodunuzu bozdurarak VIP, Coin veya Ekstra Stok kazanın!")
@app_commands.describe(kod="Bozdurmak istediğiniz promo kodu (Örn: LEAK-A1B2-C3D4)")
async def kod_kullan_command(interaction: discord.Interaction, kod: str):
    await interaction.response.defer(ephemeral=True)
    success, msg = db.redeem_promo_key(interaction.user.id, kod)
    
    embed = discord.Embed(
        title="🎟️ Promo Kod Sistemi",
        description=msg,
        color=discord.Color.green() if success else discord.Color.red()
    )
    await interaction.followup.send(embed=embed, ephemeral=True)


@bot.tree.command(name="key-olustur", description="🔑 Çekiliş ve Etkinlikler için Promo Key Üretir (Admin)")
@app_commands.default_permissions(administrator=True)
@app_commands.describe(
    tur="Ödül Türü (vip, claim, steam, coin)",
    deger="Ödül Değeri (VIP için saat, coin için miktar)",
    adet="Kaç adet key üretilsin?"
)
@app_commands.choices(tur=[
    app_commands.Choice(name="⭐ VIP Üyelik Key", value="vip"),
    app_commands.Choice(name="🪙 Coin Bakiye Key", value="coin"),
    app_commands.Choice(name="🎁 +1 Stok Hakkı Key", value="claim"),
    app_commands.Choice(name="🎮 Steam Oyun Hesabı Key", value="steam")
])
async def key_olustur_command(interaction: discord.Interaction, tur: str, deger: str = "24", adet: int = 1):
    if not is_admin_user(interaction.user):
        await interaction.response.send_message("❌ Bu komutu sadece Yöneticiler kullanabilir!", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)
    created_keys = db.create_promo_keys(reward_type=tur, reward_value=deger, count=adet)

    key_str = "\n".join([f"`{k}`" for k in created_keys])
    embed = discord.Embed(
        title="🔑 Promo Keyler Üretildi!",
        description=f"**Tür:** `{tur.upper()}` | **Değer:** `{deger}` | **Adet:** `{len(created_keys)}`\n\n**Key Listesi:**\n{key_str}",
        color=discord.Color.gold()
    )
    await interaction.followup.send(embed=embed, ephemeral=True)


@bot.tree.command(name="davetlerim", description="👥 Davet sayınızı ve VIP ödül ilerlemenizi görün")
async def davetlerim_command(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    u_data = db.get_user_data(interaction.user.id)
    invites = u_data.get("invites", 0)
    cfg = db.get_config()
    target_invites = cfg.get("invites_for_vip", 5)

    is_vip = db.is_user_vip_db(interaction.user.id)
    progress_str = "✅ **Otomatik 1 Günlük VIP Kazanıldı!**" if is_vip else f"🏆 1 Günlük VIP Ödülüne Kalan: **{max(0, target_invites - invites)} davet**"

    embed = discord.Embed(
        title=f"👥 {interaction.user.name} - Davet İstatistikleri",
        description=f"• **Toplam Davet Sayınız:** `{invites} kişi`\n• **VIP İlerleme:** {progress_str}",
        color=discord.Color.blue()
    )
    await interaction.followup.send(embed=embed, ephemeral=True)


@bot.tree.command(name="liderlik", description="🏆 En çok stok alan, coin sahibi ve davet yapan üyeler liderlik tablosu")
async def liderlik_command(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    leaderboard = db.get_leaderboard(limit=10)

    embed = discord.Embed(
        title="🏆 LeaksTr En Aktif Üyeler Liderlik Tablosu",
        description="En çok stok alan ve sunucuyu büyüten en aktif üyelerimiz:",
        color=discord.Color.gold(),
        timestamp=discord.utils.utcnow()
    )

    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    rank_text = ""
    for idx, entry in enumerate(leaderboard):
        medal = medals[idx] if idx < len(medals) else "🏅"
        u_id = entry["user_id"]
        claims = entry["claims"]
        invites = entry["invites"]
        coins = entry.get("coins", 0)
        vip_mark = "⭐" if entry["is_vip"] else ""
        rank_text += f"{medal} <@{u_id}> {vip_mark} • **{claims} Stok** | **{coins} Coin** | **{invites} Davet**\n"

    embed.add_field(name="Top 10 Üye", value=rank_text or "Henüz veri yok.", inline=False)
    await interaction.followup.send(embed=embed, ephemeral=True)


@bot.tree.command(name="dosya-stok-ekle", description="📂 .txt Dosyası yükleyerek 10.000+ stok ekler (Admin)")
@app_commands.default_permissions(administrator=True)
@app_commands.describe(servis_id="Stok eklenecek servisin ID'si", dosya="Hesapların olduğu .txt dosyası")
async def slash_dosya_stok(interaction: discord.Interaction, servis_id: str, dosya: discord.Attachment):
    if not is_admin_user(interaction.user):
        await interaction.response.send_message("❌ Bu komutu sadece Yöneticiler kullanabilir!", ephemeral=True)
        return

    service = db.get_service(servis_id)
    if not service:
        await interaction.response.send_message(f"❌ **'{servis_id}'** ID'li servis bulunamadı!", ephemeral=True)
        return

    if not dosya.filename.endswith(".txt"):
        await interaction.response.send_message("❌ Yüklenen dosya `.txt` uzantılı olmalıdır!", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)

    try:
        content_bytes = await dosya.read()
        try:
            content_str = content_bytes.decode("utf-8")
        except UnicodeDecodeError:
            content_str = content_bytes.decode("latin-1", errors="ignore")

        lines = [line.strip() for line in content_str.splitlines() if line and line.strip()]
        added_count = db.add_stock(servis_id, lines)
        total_count = db.get_stock_count(servis_id)

        embed = discord.Embed(
            title="🚀 YÜKSEK HACİMLİ STOK YÜKLENDİ!",
            description=f"**{service['name']}** servisine **{added_count:,} adet** hesap yüklendi!\n\n📊 Güncel Toplam Stok: **{total_count:,} adet**",
            color=discord.Color.green()
        )
        await interaction.followup.send(embed=embed, ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"❌ Hata: {e}", ephemeral=True)

@slash_dosya_stok.autocomplete("servis_id")
async def servis_id_autocomplete(interaction: discord.Interaction, current: str):
    services = db.get_services()
    choices = []
    for s in services:
        if current.lower() in s["id"].lower() or current.lower() in s["name"].lower():
            choices.append(app_commands.Choice(name=f"{s['emoji']} {s['name']} ({s['id']})", value=s["id"]))
    return choices[:25]


@bot.tree.command(name="panel", description="🎁 Ana Generator & Stok Mesaj Paneli Kurar (Admin)")
@app_commands.default_permissions(administrator=True)
async def panel_command(interaction: discord.Interaction):
    if not is_admin_user(interaction.user):
        await interaction.response.send_message("❌ Bu komutu sadece Yöneticiler kullanabilir!", ephemeral=True)
        return

    await create_panel_embed_and_send(interaction.channel, interaction.guild)
    await interaction.response.send_message("✅ Gelişmiş Etkileşim Paneli başarıyla kuruldu!", ephemeral=True)


@bot.tree.command(name="stok-ekle", description="📦 Bir servise yeni stok ekler (Modal Form / Çoklu Satır)")
@app_commands.default_permissions(administrator=True)
@app_commands.describe(servis_id="Stok eklenecek servisin ID'si (Örn: netflix_free)")
async def stok_ekle_command(interaction: discord.Interaction, servis_id: str):
    if not is_admin_user(interaction.user):
        await interaction.response.send_message("❌ Bu komutu sadece Yöneticiler kullanabilir!", ephemeral=True)
        return

    service = db.get_service(servis_id)
    if not service:
        services = db.get_services()
        available_ids = ", ".join([f"`{s['id']}`" for s in services])
        await interaction.response.send_message(
            f"❌ **Geçersiz Servis ID!**\nKullanılabilir ID'ler: {available_ids}",
            ephemeral=True
        )
        return

    modal = AddStockModal(service_id=servis_id, service_name=service["name"])
    await interaction.response.send_modal(modal)


@stok_ekle_command.autocomplete("servis_id")
async def stok_ekle_autocomplete(interaction: discord.Interaction, current: str):
    return await servis_id_autocomplete(interaction, current)


@bot.tree.command(name="stok-temizle", description="🗑️ Bir servisin tüm stoklarını sıfırlar")
@app_commands.default_permissions(administrator=True)
@app_commands.describe(servis_id="Stokları silinecek servisin ID'si")
async def stok_temizle_command(interaction: discord.Interaction, servis_id: str):
    if not is_admin_user(interaction.user):
        await interaction.response.send_message("❌ Bu komutu sadece Yöneticiler kullanabilir!", ephemeral=True)
        return

    service = db.get_service(servis_id)
    if not service:
        await interaction.response.send_message("❌ Geçersiz Servis ID!", ephemeral=True)
        return

    removed = db.clear_stock(servis_id)
    await interaction.response.send_message(
        f"✅ **{service['name']}** servisinden **{removed}** adet stok başarıyla temizlendi!",
        ephemeral=True
    )

@stok_temizle_command.autocomplete("servis_id")
async def stok_temizle_autocomplete(interaction: discord.Interaction, current: str):
    return await servis_id_autocomplete(interaction, current)


@bot.tree.command(name="stok-liste", description="📋 Detaylı stok listesini ve sayılarını gösterir")
@app_commands.default_permissions(administrator=True)
async def stok_liste_command(interaction: discord.Interaction):
    if not is_admin_user(interaction.user):
        await interaction.response.send_message("❌ Bu komutu sadece Yöneticiler kullanabilir!", ephemeral=True)
        return

    services = db.get_services()
    embed = discord.Embed(
        title="📋 Detaylı Stok Yönetim Paneli",
        color=discord.Color.gold(),
        timestamp=discord.utils.utcnow()
    )

    for s in services:
        count = db.get_stock_count(s["id"])
        category_str = "⭐ VIP" if s.get("category") == "vip" else "🎁 FREE"
        is_unlimited = s.get("id") in ["steam_free", "gemini_pro", "mc_vip", "tonguc_vip", "tod_tv_vip", "prime_video_vip"] or s.get("is_unlimited", False)
        is_ticket = s.get("requires_ticket", False) or s.get("id") in ["mailchecker_tool", "nitro_promo", "spotify_premium_vip"]
        
        if is_ticket:
            count_txt = "🎫 Özel Ticket"
        elif is_unlimited:
            count_txt = "∞ Sınırsız"
        else:
            count_txt = f"{count} adet"

        embed.add_field(
            name=f"{s.get('emoji', '📦')} {s['name']} (`{s['id']}`)",
            value=f"• Tür: **{category_str}**\n• Durum: **{count_txt}**",
            inline=True
        )

    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="vip-yönet", description="👑 Bir üyeye VIP statüsü verir veya kaldırır (Süresiz)")
@app_commands.default_permissions(administrator=True)
@app_commands.describe(kullanici="VIP durumu değiştirilecek üye", vip_durum="Evet veya Hayır")
async def vip_yonet_command(interaction: discord.Interaction, kullanici: discord.User, vip_durum: bool):
    if not is_admin_user(interaction.user):
        await interaction.response.send_message("❌ Bu komutu sadece Yöneticiler kullanabilir!", ephemeral=True)
        return

    db.set_user_vip(kullanici.id, vip_durum, duration_hours=0)
    txt = "⭐ **Süresiz VIP Verildi**" if vip_durum else "❌ **VIP Kaldırıldı**"
    await interaction.response.send_message(f"✅ {kullanici.mention} için yeni durum: {txt}", ephemeral=True)


@bot.tree.command(name="hak-sifirla", description="🔄 Bir kullanıcının günlük stok alma bekleme süresini sıfırlar")
@app_commands.default_permissions(administrator=True)
@app_commands.describe(kullanici="Bekleme süresi sıfırlanacak üye")
async def hak_sifirla_command(interaction: discord.Interaction, kullanici: discord.User):
    if not is_admin_user(interaction.user):
        await interaction.response.send_message("❌ Bu komutu sadece Yöneticiler kullanabilir!", ephemeral=True)
        return

    db.reset_user_cooldown(kullanici.id)
    await interaction.response.send_message(f"✅ {kullanici.mention} kullanıcısının günlük stok alma hakkı sıfırlandı!", ephemeral=True)


@bot.tree.command(name="ayarlar", description="⚙️ Bot ayarlarını değiştirir (Limitler, Anti-Alt yaş sınırı vb.)")
@app_commands.default_permissions(administrator=True)
@app_commands.describe(
    cooldown_saat="Kaç saatte bir stok alınabilsin? (Varsayılan: 24)",
    free_daily_limit="Free üyelerin günlük alabileceği stok sayısı (Varsayılan: 1)",
    vip_daily_limit="VIP üyelerin günlük alabileceği stok sayısı (Varsayılan: 2)",
    booster_daily_limit="Nitro Booster üyelerin günlük alabileceği stok sayısı (Varsayılan: 3)",
    durum_sarti="Kullanıcı durumunda olması gereken kelime (Örn: LeaksTr)",
    min_hesap_yasi="Anti-Alt için minimum hesap yaşı (gün, Varsayılan: 7)",
    davet_vip_hedef="Kaç davette otomatik VIP verilsin? (Varsayılan: 5)",
    vip_rol="VIP rolü",
    log_kanali="Stok teslimat loglarının gönderileceği kanal"
)
async def ayarlar_command(
    interaction: discord.Interaction,
    cooldown_saat: int = None,
    free_daily_limit: int = None,
    vip_daily_limit: int = None,
    booster_daily_limit: int = None,
    durum_sarti: str = None,
    min_hesap_yasi: int = None,
    davet_vip_hedef: int = None,
    vip_rol: discord.Role = None,
    log_kanali: discord.TextChannel = None
):
    if not is_admin_user(interaction.user):
        await interaction.response.send_message("❌ Bu komutu sadece Yöneticiler kullanabilir!", ephemeral=True)
        return

    changes = []
    if cooldown_saat is not None:
        db.update_config("cooldown_hours", cooldown_saat)
        changes.append(f"⏱️ Bekleme Süresi: **{cooldown_saat} saat**")
    if free_daily_limit is not None:
        db.update_config("free_daily_limit", free_daily_limit)
        changes.append(f"🎁 Free Günlük Limit: **{free_daily_limit} adet**")
    if vip_daily_limit is not None:
        db.update_config("vip_daily_limit", vip_daily_limit)
        changes.append(f"⭐ VIP Günlük Limit: **{vip_daily_limit} adet**")
    if booster_daily_limit is not None:
        db.update_config("booster_daily_limit", booster_daily_limit)
        changes.append(f"🚀 Booster Günlük Limit: **{booster_daily_limit} adet**")
    if durum_sarti is not None:
        db.update_config("required_status", durum_sarti)
        changes.append(f"💬 Durum Şartı Kelimesi: **{durum_sarti}**")
    if min_hesap_yasi is not None:
        db.update_config("min_account_age_days", min_hesap_yasi)
        changes.append(f"🛡️ Anti-Alt Min Hesap Yaşı: **{min_hesap_yasi} gün**")
    if davet_vip_hedef is not None:
        db.update_config("invites_for_vip", davet_vip_hedef)
        changes.append(f"👥 VIP İçin Davet Hedefi: **{davet_vip_hedef} davet**")
    if vip_rol is not None:
        db.update_config("vip_role_id", vip_rol.id)
        changes.append(f"👑 VIP Rolü: {vip_rol.mention}")
    if log_kanali is not None:
        db.update_config("log_channel_id", log_kanali.id)
        changes.append(f"📜 Log Kanalı: {log_kanali.mention}")

    if not changes:
        cfg = db.get_config()
        embed = discord.Embed(title="⚙️ Güncel Bot Ayarları", color=discord.Color.blue())
        embed.add_field(name="⏱️ Cooldown (Saat)", value=f"{cfg.get('cooldown_hours', 24)} saat", inline=True)
        embed.add_field(name="🎁 Free Limit", value=f"{cfg.get('free_daily_limit', 1)} adet", inline=True)
        embed.add_field(name="⭐ VIP Limit", value=f"{cfg.get('vip_daily_limit', 2)} adet", inline=True)
        embed.add_field(name="🚀 Booster Limit", value=f"{cfg.get('booster_daily_limit', 3)} adet", inline=True)
        embed.add_field(name="💬 Durum Şartı", value=f"`{cfg.get('required_status', 'LeaksTr')}`", inline=True)
        embed.add_field(name="🛡️ Anti-Alt Min Yaş", value=f"{cfg.get('min_account_age_days', 7)} gün", inline=True)
        embed.add_field(name="👥 VIP Davet Hedefi", value=f"{cfg.get('invites_for_vip', 5)} davet", inline=True)
        embed.add_field(name="📜 Log Kanal ID", value=f"`{cfg.get('log_channel_id', 0)}`", inline=True)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    embed = discord.Embed(
        title="⚙️ Ayarlar Güncellendi",
        description="\n".join(changes),
        color=discord.Color.green()
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)


# --- MAIN ENTRY POINT ---
if __name__ == "__main__":
    if not TOKEN:
        print("❌ HATA: DISCORD_TOKEN .env dosyasında bulunamadı!")
        print("Lütfen .env dosyasını açıp bot tokeninizi girin.")
    else:
        bot.run(TOKEN)
