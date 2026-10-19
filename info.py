import os
import requests
from io import BytesIO
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
import time
import logging
from html import escape
import json
import re
import urllib.parse
import binascii
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

API_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BOT_USERNAME = "fuddjsshedffjfjdjhshsbot"

# Jika token tidak disediakan lewat environment variable, minta secara interaktif.
# Token tidak disimpan ke file atau repository.
if not API_TOKEN:
    from getpass import getpass
    API_TOKEN = getpass("Masukkan token Telegram dari @BotFather: ").strip()

if not API_TOKEN:
    raise RuntimeError("Token Telegram kosong. Jalankan ulang dan masukkan token yang valid.")

bot = telebot.TeleBot(API_TOKEN)

# ============ LOGGING ============
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# ============ CONFIGURATION ============
VALID_REGIONS = ["ind", "sg", "br", "ru", "id", "tw", "us", "vn", "th", "me", "pk", "cis", "bd", "na"]

# ============================================================
# DIRECT API ENDPOINTS (as provided by you)
# ============================================================

# 1. STAR PLAYER INFO API - Source: STAR_RDP
STAR_PLAYER_INFO_API = "https://star-info-api.lovable.app/functions/v1/info-api/accinfo?uid={uid}"

# 2. GUEST UID PASSWORD TO LEVEL INFO API - Source: STAR_RDP
GUEST_LEVEL_API = "https://guest-info.stargmr.pro/api/public/lookup?uid={uid}&password={password}"

# 3. BAN CHECK API - Source: killersharmabot
BANCHECK_API = "https://info.killersharmabot.online/bancheck?uid={uid}"

# 4. WISHLIST API - Source: killersharmabot
WISHLIST_API = "https://info.killersharmabot.online/wishlist?uid={uid}"

# 5. GUILD INFO API - Source: STAR_RDP
GUILD_API = "https://star-guild-info.lovable.app/api/public/info?clan_id={clan_id}&region={region}"

# 6. JWT TOKEN API - Source: STAR_RDP
JWT_API = "https://ff-jwt-gen-api.lovable.app/api/public/token?uid={uid}&password={password}"

# 7. ACCESS TOKEN TO JWT API - Source: STAR_RDP
ACCESS_API = "https://access.killersharmabot.online/access?access_token={access_token}"

# 8. EAT TO ACCESS TOKEN API - Source: Garena
EAT_API = "https://api-otrss.garena.com/support/callback/?access_token={eat_token}"

# 9. BIO UPDATE API - Source: STAR_RDP
BIO_API = "https://star-bio-api.lovable.app/api/public/bio-upload?bio={bio}&uid={uid}&password={password}"

# 10. ICON PNG API - Source: STAR_RDP
ICON_PNG_API = "https://star-icon-png.lovable.app/png?icon_id={icon_id}"

# ============================================================
# IMAGE APIs - Source: Aditya FF Apis / killersharmabot
# ============================================================

OUTFIT_API_URL = "https://image.killersharmabot.online/outfit-image?avatar_id={avatar_id}&clothes={clothes}"
BANNER_API_URL = "https://image.killersharmabot.online/banner-image?headPic={headPic}&bannerId={bannerId}&name={name}&level={level}&guild={guild}&pinId={pinId}&celebrity={celebrity}&frame={frame}"
AVATAR_API_URL = "https://ffoutfitapis.vercel.app/avatar-image?uid={uid}&region={region}&key=99day"

# 11. ITEM APIs - Source: item-image-api
ITEM_IMAGE_API = "https://item-image-api.onrender.com/item-image?id={item_id}&key=NRCODEX"
ITEM_INFO_API = "https://item-image-api.onrender.com/iteminfo?id={item_id}"

# ============ HELPER FUNCTIONS ============

def is_valid_uid(uid):
    return uid.isdigit() and 8 <= len(uid) <= 11

def escape_markdown(text):
    escape_chars = '_*[]()~`>#+-=|{}.!'
    return ''.join(['\\' + char if char in escape_chars else char for char in str(text)])

def format_timestamp(ts):
    try:
        if ts and ts != 'ɴ/ᴀ' and ts != '':
            return datetime.utcfromtimestamp(int(ts)).strftime('%d-%m-%Y %H:%M:%S')
        return 'ɴ/ᴀ'
    except:
        return 'ɴ/ᴀ'

def encode_for_url(text):
    if text and text != 'ɴ/ᴀ':
        return urllib.parse.quote(str(text))
    return ''

def safe_get_url(url, timeout=15):
    try:
        logger.info(f"Requesting: {url}")
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return response
    except Exception as e:
        logger.error(f"Request error: {e}")
        return None

def download_image(url):
    try:
        response = safe_get_url(url)
        if response:
            return response.content
        return None
    except Exception as e:
        logger.error(f"Image download error: {e}")
        return None

# ============ API FUNCTIONS ============

def fetch_player_data_star(uid):
    """API 1: STAR Player Info - STAR_RDP"""
    url = STAR_PLAYER_INFO_API.format(uid=uid)
    response = safe_get_url(url)
    if not response:
        return None
    try:
        return response.json()
    except:
        return None

def fetch_guest_level(uid, password):
    """API 2: Guest Level Info - STAR_RDP"""
    url = GUEST_LEVEL_API.format(uid=uid, password=password)
    response = safe_get_url(url)
    if not response:
        return None
    return response.json()

def fetch_bancheck(search_param):
    """API 3: Ban Check - killersharmabot"""
    if search_param.isdigit():
        url = BANCHECK_API.format(uid=search_param)
    else:
        url = BANCHECK_API.replace("uid={uid}", f"name={urllib.parse.quote(search_param)}")
    response = safe_get_url(url)
    if not response:
        return None
    return response.json()

def fetch_wishlist(search_param):
    """API 4: Wishlist - killersharmabot"""
    if search_param.isdigit():
        url = WISHLIST_API.format(uid=search_param)
    else:
        url = WISHLIST_API.replace("uid={uid}", f"name={urllib.parse.quote(search_param)}")
    response = safe_get_url(url)
    if not response:
        return None
    return response.json()

def fetch_guild_info(clan_id, region):
    """API 5: Guild Info - STAR_RDP"""
    url = GUILD_API.format(clan_id=clan_id, region=region.upper())
    response = safe_get_url(url)
    if not response:
        return None
    return response.json()

def generate_jwt(uid, password):
    """API 6: JWT Token - STAR_RDP"""
    url = JWT_API.format(uid=uid, password=password)
    response = safe_get_url(url)
    if not response:
        return None
    return response.json()

def generate_jwt_from_access(access_token):
    """API 7: Access to JWT - STAR_RDP"""
    url = ACCESS_API.format(access_token=access_token)
    response = safe_get_url(url)
    if not response:
        return None
    return response.json()

def generate_jwt_from_eat(eat_token):
    """API 8: EAT to Access - Garena"""
    url = EAT_API.format(eat_token=eat_token)
    response = safe_get_url(url)
    if not response:
        return None
    return response.json()

def upload_bio(bio, uid=None, password=None, jwt=None, access=None):
    """API 9: Bio Update - STAR_RDP"""
    if uid and password:
        url = f"https://star-bio-api.lovable.app/api/public/bio-upload?bio={urllib.parse.quote(bio)}&uid={uid}&password={password}"
    elif jwt:
        url = f"https://star-bio-api.lovable.app/api/public/bio-upload?bio={urllib.parse.quote(bio)}&jwt={jwt}"
    elif access:
        url = f"https://star-bio-api.lovable.app/api/public/bio-upload?bio={urllib.parse.quote(bio)}&access={access}"
    else:
        return None
    response = safe_get_url(url)
    if not response:
        return None
    return response.json()

def fetch_icon_png(icon_id):
    """API 10: Icon PNG - STAR_RDP"""
    url = ICON_PNG_API.format(icon_id=icon_id)
    return download_image(url)

def fetch_item_info(item_id):
    """API 11: Item Info - item-image-api"""
    url = ITEM_INFO_API.format(item_id=item_id)
    response = safe_get_url(url)
    if not response:
        return None
    return response.json()

def get_item_image(item_id):
    """API 12: Item Image - item-image-api"""
    url = ITEM_IMAGE_API.format(item_id=item_id)
    return download_image(url)

# ============ BOT COMMANDS (With Dual Support) ============

@bot.message_handler(commands=['start', 'help'])
def start_command(message):
    try:
        markup = InlineKeyboardMarkup(row_width=1)
        add_to_group_btn = InlineKeyboardButton(
            text="➕ ADD TO GROUP",
            url=f"https://t.me/{BOT_USERNAME}?startgroup=true"
        )
        markup.add(add_to_group_btn)
        
        start_msg = """<b>🎮 FREE FIRE PLAYER INFO BOT 🎮</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
<b>📝 SYSTEM OVERVIEW</b>
Welcome to the Free Fire Player Information System! This bot provides comprehensive player intelligence and account analytics for Free Fire across all global servers.

<b>🤖 MAIN COMMANDS</b>
• <b>Get</b> [UID/Name] - Full player profile with all details
• <b>Banner</b> [UID/Name] - View player's banner
• <b>Outfit</b> [UID/Name] - View player's outfits
• <b>Wishlist</b> [UID/Name] - Player's wishlist with item images
• <b>Region</b> [UID/Name] - Server region information
• <b>Level</b> [UID/Name] [Password] - Level progression analysis
• <b>Isbanned</b> [UID/Name] - Account security status
• <b>Token</b> [UID] [Password] - Generate login tokens
• <b>Access</b> [AccessToken] - Generate token from access token
• <b>Eat</b> [EatToken] - Generate token from EAT token
• <b>Icon</b> [IconID] - Get icon PNG image
• <b>Item</b> [item_id] - Search Items Information with Image
• <b>Help</b> - Complete command manual

<b>📊 DATA COVERAGE</b>
• Complete Player Profiles
• Equipment & Skills
• Battle Statistics
• Guild Information
• Craftland Maps
• Wishlist Items
• Ban Status
• Update player's bio signature
• Region Detection
• Items Database - Search items by ID or Icon Name
• Icon PNG Generator

<b>🌍 SUPPORTED REGIONS</b>
All global servers including: IND, BR, US, SAC, NA, SG, RU, ID, TW, VN, TH, ME, PK, BD, EUROPE

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Type Help for detailed command reference
Status: ✅ Operational | API: ✅ Connected | Database: ✅ Online

<b>🔰 CREDIT: @bselius</b>
<b>🔰 DEVELOPER: @bselius</b>"""

        # ⚠️ IMPORTANT: parse_mode="HTML" add karo
        bot.reply_to(message, start_msg, reply_markup=markup, parse_mode="HTML")
        
    except Exception as e:
        logger.error(f"Start command error: {str(e)}")
        bot.reply_to(message, "❌ ᴀɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ.")
        
# ============ COMMAND WITH SLASH ============

@bot.message_handler(commands=['info', 'get'])
def info_command(message):
    try:
        cmd_parts = message.text.split()
        if len(cmd_parts) < 2:
            bot.reply_to(message, "Usage: /info <uid>\nExample: /info 12345678")
            return

        uid = cmd_parts[1]
        if not is_valid_uid(uid):
            bot.reply_to(message, "ɪɴᴠᴀʟɪᴅ ᴜɪᴅ! ᴜɪᴅ ᴍᴜsᴛ ʙᴇ 8-11 ᴅɪɢɪᴛs.")
            return

        processing_msg = bot.reply_to(message, "🔍 ғᴇᴛᴄʜɪɴɢ ᴘʟᴀʏᴇʀ ɪɴғᴏ...")

        data = fetch_player_data_star(uid)
        if not data or 'basic_info' not in data:
            bot.edit_message_text(
                "❌ ᴘʟᴀʏᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ.",
                processing_msg.chat.id,
                processing_msg.message_id
            )
            return

        basic = data['basic_info']
        captain = data.get('captain_basic_info', {})
        clan = data.get('clan_basic_info', {})
        credit = data.get('credit_score_info', {})
        pet = data.get('pet_info', {})
        profile = data.get('profile_info', {})
        social = data.get('social_info', {})

        nickname = basic.get('nickname', 'ɴ/ᴀ')
        region = basic.get('region', 'ɴ/ᴀ')
        last_login = format_timestamp(basic.get('last_login_at'))
        ban_status = "✅ ɴᴏᴛ ʙᴀɴɴᴇᴅ"

        clothes_ids = profile.get('clothes', [])
        avatar_id = profile.get('avatar_id', '')
        prime_level = basic.get('prime_info', {}).get('prime_level', 'ɴ/ᴀ')

        info_text = f"""🎮 ᴘʟᴀʏᴇʀ ɪɴғᴏʀᴍᴀᴛɪᴏɴ
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👤 ɴɪᴄᴋɴᴀᴍᴇ: <code>{escape(nickname)}</code>
🆔 ᴜɪᴅ: <code>{uid}</code>
🌍 ʀᴇɢɪᴏɴ: <code>{region}</code>
📊 ʟᴇᴠᴇʟ: <code>{basic.get('level', 'ɴ/ᴀ')}</code>
⭐ ᴇxᴘ: <code>{basic.get('exp', 'ɴ/ᴀ')}</code>
👍 ʟɪᴋᴇs: <code>{basic.get('liked', 'ɴ/ᴀ')}</code>
🏅 ʀᴀɴᴋ: <code>{basic.get('rank', 'ɴ/ᴀ')}</code>
⭐ ʀᴀɴᴋɪɴɢ ᴘᴏɪɴᴛs: <code>{basic.get('ranking_points', 'ɴ/ᴀ')}</code>
🏆 ᴄs ʀᴀɴᴋ: <code>{basic.get('cs_rank', 'ɴ/ᴀ')}</code>
🔒 ʙᴀɴ sᴛᴀᴛᴜs: <code>{ban_status}</code>
📌 ᴛɪᴛʟᴇ: <code>{basic.get('title', 'ɴ/ᴀ')}</code>
🖼️ ʜᴇᴀᴅᴘɪᴄ: <code>{basic.get('head_pic', 'ɴ/ᴀ')}</code>
🎨 ʙᴀɴɴᴇʀ ɪᴅ: <code>{basic.get('banner_id', 'ɴ/ᴀ')}</code>
🏅 ʙᴀᴅɢᴇ ᴄᴏᴜɴᴛ: <code>{basic.get('badge_cnt', 'ɴ/ᴀ')}</code>
📦 ᴘʀɪᴍᴇ ʟᴇᴠᴇʟ: <code>{prime_level}</code>
📱 ʀᴇʟᴇᴀsᴇ ᴠᴇʀsɪᴏɴ: <code>{basic.get('release_version', 'ɴ/ᴀ')}</code>
📅 sᴇᴀsᴏɴ: <code>{basic.get('season_id', 'ɴ/ᴀ')}</code>
📅 ʟᴀsᴛ ʟᴏɢɪɴ: <code>{last_login}</code>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👑 ᴄʟᴀɴ ɪɴғᴏʀᴍᴀᴛɪᴏɴ
🏠 ᴄʟᴀɴ ɴᴀᴍᴇ: <code>{escape(clan.get('clan_name', 'ɴ/ᴀ'))}</code>
🆔 ᴄʟᴀɴ ɪᴅ: <code>{clan.get('clan_id', 'ɴ/ᴀ')}</code>
📊 ᴄʟᴀɴ ʟᴇᴠᴇʟ: <code>{clan.get('clan_level', 'ɴ/ᴀ')}</code>
👥 ᴍᴇᴍʙᴇʀs: <code>{clan.get('member_num', 'ɴ/ᴀ')}</code>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💳 ᴄʀᴇᴅɪᴛ sᴄᴏʀᴇ
⭐ ᴄʀᴇᴅɪᴛ sᴄᴏʀᴇ: <code>{credit.get('credit_score', 'ɴ/ᴀ')}</code>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🐾 ᴘᴇᴛ ɪɴғᴏʀᴍᴀᴛɪᴏɴ
🐕 ɴᴀᴍᴇ: <code>{escape(pet.get('name', 'ɴ/ᴀ'))}</code>
📊 ʟᴇᴠᴇʟ: <code>{pet.get('level', 'ɴ/ᴀ')}</code>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎭 ᴘʀᴏғɪʟᴇ ɪɴғᴏʀᴍᴀᴛɪᴏɴ
👤 ᴀᴠᴀᴛᴀʀ ɪᴅ: <code>{profile.get('avatar_id', 'ɴ/ᴀ')}</code>
👕 ᴄʟᴏᴛʜᴇs: <code>{', '.join(str(c) for c in clothes_ids) if clothes_ids else 'ɴ/ᴀ'}</code>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👤 ᴄᴀᴘᴛᴀɪɴ ɪɴғᴏʀᴍᴀᴛɪᴏɴ
👤 ɴᴀᴍᴇ: <code>{escape(captain.get('nickname', 'ɴ/ᴀ'))}</code>
🆔 ᴜɪᴅ: <code>{captain.get('account_id', 'ɴ/ᴀ')}</code>
📊 ʟᴇᴠᴇʟ: <code>{captain.get('level', 'ɴ/ᴀ')}</code>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 sᴏᴄɪᴀʟ ɪɴғᴏʀᴍᴀᴛɪᴏɴ
💬 ʟᴀɴɢᴜᴀɢᴇ: <code>{social.get('language', 'ɴ/ᴀ')}</code>
✍️ sɪɢɴᴀᴛᴜʀᴇ: <code>{escape(social.get('signature', 'ɴ/ᴀ'))}</code>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔰 ᴄʀᴇᴅɪᴛ: @bselius"""

        bot.delete_message(processing_msg.chat.id, processing_msg.message_id)
        bot.send_message(message.chat.id, info_text, parse_mode="HTML")

        # Send Images
        images_to_send = []

        if avatar_id and clothes_ids:
            outfit_url = OUTFIT_API_URL.format(
                avatar_id=avatar_id,
                clothes=','.join(str(c) for c in clothes_ids)
            )
            img = download_image(outfit_url)
            if img:
                images_to_send.append(("👕 ᴏᴜᴛғɪᴛ", img))

        avatar_url = AVATAR_API_URL.format(uid=uid, region=region)
        img = download_image(avatar_url)
        if img:
            images_to_send.append(("🖼️ ᴀᴠᴀᴛᴀʀ", img))

        headpic = basic.get('head_pic', '')
        banner_id = basic.get('banner_id', '')
        if headpic and banner_id:
            name = encode_for_url(nickname)
            guild = encode_for_url(clan.get('clan_name', ''))
            pin_id = basic.get('pin_id', '')
            celebrity = basic.get('celebrity_status', 0)
            frame = "true" if prime_level >= 8 else "false"
            banner_url = BANNER_API_URL.format(
                headPic=headpic,
                bannerId=banner_id,
                name=name,
                level=basic.get('level', 2),
                guild=guild,
                pinId=pin_id,
                celebrity=celebrity,
                frame=frame
            )
            img = download_image(banner_url)
            if img:
                images_to_send.append(("🎨 ʙᴀɴɴᴇʀ", img))

        for caption, img in images_to_send:
            try:
                bot.send_photo(
                    message.chat.id,
                    img,
                    caption=f"{caption}\n👤 {escape(nickname)}\n🔰 @bselius",
                    parse_mode="HTML"
                )
            except Exception as e:
                logger.error(f"Image send error: {e}")

    except Exception as e:
        bot.reply_to(message, f"❌ ᴇʀʀᴏʀ: {str(e)}")

@bot.message_handler(commands=['level'])
def level_command(message):
    try:
        parts = message.text.split()
        if len(parts) < 3:
            bot.reply_to(message, "Usage: /level <uid> <password>\nExample: /level 4561074788 STAR-WKK6JB4AF-CORE")
            return
        uid = parts[1]
        password = parts[2]
        if not is_valid_uid(uid):
            bot.reply_to(message, "❌ ɪɴᴠᴀʟɪᴅ ᴜɪᴅ.")
            return
        processing = bot.reply_to(message, "🔍 ғᴇᴛᴄʜɪɴɢ ʟᴇᴠᴇʟ...")
        data = fetch_guest_level(uid, password)
        if not data or not data.get('success'):
            bot.edit_message_text("❌ ᴘʟᴀʏᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ.", processing.chat.id, processing.message_id)
            return
        
        player = data.get('player', {})
        text = f"""📊 ʟᴇᴠᴇʟ ᴘʀᴏɢʀᴇssɪᴏɴ
━━━━━━━━━━━━━━━━━━━━━━
👤 ɴᴀᴍᴇ: <code>{escape(data.get('nickname', 'ɴ/ᴀ'))}</code>
🆔 ᴜɪᴅ: <code>{data.get('uid', 'ɴ/ᴀ')}</code>
🌍 ʀᴇɢɪᴏɴ: <code>{data.get('region', 'ɴ/ᴀ')}</code>
📊 ʟᴇᴠᴇʟ: <code>{data.get('level', 'ɴ/ᴀ')}</code>
⭐ ᴄᴜʀʀᴇɴᴛ ᴇxᴘ: <code>{player.get('exp', 'ɴ/ᴀ')}</code>
📌 ᴇxᴘ ɴᴇᴇᴅᴇᴅ: <code>{player.get('expNeeded', 'ɴ/ᴀ')}</code>
📈 ᴘʀᴏɢʀᴇss: <code>{player.get('levelProgress', 'ɴ/ᴀ')}</code>
🏅 ʀᴀɴᴋ: <code>{player.get('rankingName', 'ɴ/ᴀ')}</code>
━━━━━━━━━━━━━━━━━━━━━━
🔰 @bselius"""
        bot.delete_message(processing.chat.id, processing.message_id)
        bot.send_message(message.chat.id, text, parse_mode="HTML")
    except Exception as e:
        bot.reply_to(message, f"❌ ᴇʀʀᴏʀ: {str(e)}")

@bot.message_handler(commands=['token'])
def token_command(message):
    try:
        parts = message.text.split()
        if len(parts) < 3:
            bot.reply_to(message, "Usage: /token <uid> <password>\nExample: /token 4561074788 IUU-AF-CORE")
            return
        uid = parts[1]
        password = parts[2]
        if not is_valid_uid(uid):
            bot.reply_to(message, "❌ ɪɴᴠᴀʟɪᴅ ᴜɪᴅ.")
            return
        processing_msg = bot.reply_to(message, "🔄 ɢᴇɴᴇʀᴀᴛɪɴɢ ᴛᴏᴋᴇɴs...")
        result = generate_jwt(uid, password)
        if not result:
            bot.edit_message_text("❌ ғᴀɪʟᴇᴅ ᴛᴏ ɢᴇɴᴇʀᴀᴛᴇ ᴛᴏᴋᴇɴ.", processing_msg.chat.id, processing_msg.message_id)
            return
        
        # Extract all fields from response
        account_id = result.get('accountId', 'ɴ/ᴀ')
        account_name = result.get('nickname', 'ɴ/ᴀ')
        region = result.get('region', 'ɴ/ᴀ')
        uid_data = result.get('uid', 'ɴ/ᴀ')
        open_id = result.get('open_id', 'ɴ/ᴀ')
        access_token = result.get('access_token', 'ɴ/ᴀ')
        token = result.get('token', 'ɴ/ᴀ')
        refresh_token = result.get('refresh_token', 'ɴ/ᴀ')
        token_type = result.get('token_type', 'ɴ/ᴀ')
        expires_in = result.get('expires_in', 'ɴ/ᴀ')
        expiry_time = result.get('expiry_time', 'ɴ/ᴀ')
        create_time = result.get('create_time', 'ɴ/ᴀ')
        refresh_expiry = result.get('refresh_expiry_time', 'ɴ/ᴀ')
        ip_region = result.get('ipRegion', 'ɴ/ᴀ')
        lock_region = result.get('lockRegion', 'ɴ/ᴀ')
        noti_region = result.get('notiRegion', 'ɴ/ᴀ')
        main_platform = result.get('main_active_platform', 'ɴ/ᴀ')
        platform = result.get('platform', 'ɴ/ᴀ')
        scope = result.get('scope', [])
        server_url = result.get('serverUrl', 'ɴ/ᴀ')
        ttl = result.get('ttl', 'ɴ/ᴀ')
        agora_env = result.get('agoraEnvironment', 'ɴ/ᴀ')
        
        # Format scope list
        scope_str = ', '.join(scope) if scope else 'ɴ/ᴀ'
        
        token_info = f"""┌ <b>ᴛᴏᴋᴇɴ ɪɴғᴏʀᴍᴀᴛɪᴏɴ</b>
├─ <b>ᴀᴄᴄᴏᴜɴᴛ ɪɴғᴏ</b>
│  ├─ ᴀᴄᴄᴏᴜɴᴛ ɪᴅ: <code>{account_id}</code>
│  ├─ ɴɪᴄᴋɴᴀᴍᴇ: <code>{escape(account_name)}</code>
│  ├─ ʀᴇɢɪᴏɴ: <code>{region}</code>
│  └─ ᴜɪᴅ: <code>{uid_data}</code>
├─ <b>ᴛᴏᴋᴇɴ ᴅᴇᴛᴀɪʟs</b>
│  ├─ ᴛᴏᴋᴇɴ: <code>{token}</code>
│  ├─ ᴀᴄᴄᴇss ᴛᴏᴋᴇɴ: <code>{access_token}</code>
│  ├─ ʀᴇғʀᴇsʜ ᴛᴏᴋᴇɴ: <code>{refresh_token}</code>
│  ├─ ᴛᴏᴋᴇɴ ᴛʏᴘᴇ: <code>{token_type}</code>
│  └─ ᴛᴛʟ: <code>{ttl}</code>
├─ <b>ᴛɪᴍᴇsᴛᴀᴍᴘs</b>
│  ├─ ᴄʀᴇᴀᴛᴇ ᴛɪᴍᴇ: <code>{create_time}</code>
│  ├─ ᴇxᴘɪʀᴇs ɪɴ: <code>{expires_in}</code>
│  ├─ ᴇxᴘɪʀʏ ᴛɪᴍᴇ: <code>{expiry_time}</code>
│  └─ ʀᴇғʀᴇsʜ ᴇxᴘɪʀʏ: <code>{refresh_expiry}</code>
├─ <b>ʀᴇɢɪᴏɴ ɪɴғᴏ</b>
│  ├─ ɪᴘ ʀᴇɢɪᴏɴ: <code>{ip_region}</code>
│  ├─ ʟᴏᴄᴋ ʀᴇɢɪᴏɴ: <code>{lock_region}</code>
│  └─ ɴᴏᴛɪ ʀᴇɢɪᴏɴ: <code>{noti_region}</code>
├─ <b>ᴘʟᴀᴛғᴏʀᴍ ɪɴғᴏ</b>
│  ├─ ᴍᴀɪɴ ᴘʟᴀᴛғᴏʀᴍ: <code>{main_platform}</code>
│  ├─ ᴘʟᴀᴛғᴏʀᴍ: <code>{platform}</code>
│  └─ ᴀɢᴏʀᴀ ᴇɴᴠ: <code>{agora_env}</code>
├─ <b>ᴏᴛʜᴇʀ ɪɴғᴏ</b>
│  ├─ ᴏᴘᴇɴ ɪᴅ: <code>{open_id}</code>
│  ├─ sᴄᴏᴘᴇ: <code>{scope_str}</code>
│  └─ sᴇʀᴠᴇʀ: <code>{server_url}</code>
└─ <b>🔰 ᴄʀᴇᴅɪᴛ: @bselius</b>"""

        bot.delete_message(processing_msg.chat.id, processing_msg.message_id)
        bot.send_message(message.chat.id, token_info, parse_mode="HTML")
        
    except Exception as e:
        bot.reply_to(message, f"❌ ᴇʀʀᴏʀ: {str(e)}")
        
@bot.message_handler(commands=['icon'])
def icon_command(message):
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "Usage: /icon <icon_id>\nExample: /icon 909000010")
            return
        icon_id = parts[1]
        if not icon_id.isdigit():
            bot.reply_to(message, "❌ ɪɴᴠᴀʟɪᴅ ɪᴄᴏɴ ɪᴅ.")
            return
        
        processing = bot.reply_to(message, "🖼️ ғᴇᴛᴄʜɪɴɢ ɪᴄᴏɴ...")
        img = fetch_icon_png(icon_id)
        
        bot.delete_message(processing.chat.id, processing.message_id)
        
        if img:
            bot.send_photo(
                message.chat.id,
                img,
                caption=f"🖼️ ɪᴄᴏɴ PNG\n📛 ɪᴅ: <code>{icon_id}</code>\n🔰 @bselius",
                parse_mode="HTML"
            )
        else:
            bot.reply_to(message, f"❌ ɪᴄᴏɴ ɴᴏᴛ ғᴏᴜɴᴅ.\nɪᴅ: {icon_id}")
            
    except Exception as e:
        bot.reply_to(message, f"❌ ᴇʀʀᴏʀ: {str(e)}")

@bot.message_handler(commands=['item'])
def item_command(message):
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "Usage: /item <item_id>")
            return
        item_id = parts[1]
        if not item_id.isdigit():
            bot.reply_to(message, "❌ ɪɴᴠᴀʟɪᴅ ɪᴛᴇᴍ ɪᴅ.")
            return
        processing = bot.reply_to(message, "🔍 ғᴇᴛᴄʜɪɴɢ ɪᴛᴇᴍ...")
        
        item_info = fetch_item_info(item_id)
        if not item_info:
            bot.edit_message_text("❌ ɪᴛᴇᴍ ɴᴏᴛ ғᴏᴜɴᴅ.", processing.chat.id, processing.message_id)
            return
        
        img = get_item_image(item_id)
        
        text = f"""📦 ɪᴛᴇᴍ ɪɴғᴏʀᴍᴀᴛɪᴏɴ
━━━━━━━━━━━━━━━━━━━━━━
🆔 ɪᴅ: <code>{item_info.get('Id', 'ɴ/ᴀ')}</code>
📛 ɴᴀᴍᴇ: <code>{escape(item_info.get('Name', 'ɴ/ᴀ'))}</code>
⭐ ʀᴀʀɪᴛʏ: <code>{item_info.get('Rare', 'ɴ/ᴀ')}</code>
🎯 ᴛʏᴘᴇ: <code>{item_info.get('Type', 'ɴ/ᴀ')}</code>
🏷️ ᴄᴀᴛᴇɢᴏʀʏ: <code>{item_info.get('Category', 'ɴ/ᴀ')}</code>
💎 ᴘʀɪᴄᴇ: <code>{item_info.get('Price', 'ɴ/ᴀ')}</code>
━━━━━━━━━━━━━━━━━━━━━━
🔰 @bselius"""
        
        bot.delete_message(processing.chat.id, processing.message_id)
        
        if img:
            bot.send_photo(
                message.chat.id,
                img,
                caption=text,
                parse_mode="HTML"
            )
        else:
            bot.send_message(message.chat.id, text, parse_mode="HTML")
            
    except Exception as e:
        bot.reply_to(message, f"❌ ᴇʀʀᴏʀ: {str(e)}")

@bot.message_handler(commands=['banner'])
def banner_command(message):
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "Usage: /banner <uid>")
            return
        uid = parts[1]
        if not is_valid_uid(uid):
            bot.reply_to(message, "❌ ɪɴᴠᴀʟɪᴅ ᴜɪᴅ.")
            return
        processing = bot.reply_to(message, "🔍 ғᴇᴛᴄʜɪɴɢ ʙᴀɴɴᴇʀ...")
        data = fetch_player_data_star(uid)
        if not data or 'basic_info' not in data:
            bot.edit_message_text("❌ ᴘʟᴀʏᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ.", processing.chat.id, processing.message_id)
            return
        basic = data['basic_info']
        clan = data.get('clan_basic_info', {})
        nickname = basic.get('nickname', 'ɴ/ᴀ')
        headpic = basic.get('head_pic', '')
        banner_id = basic.get('banner_id', '')
        if not headpic or not banner_id:
            bot.edit_message_text("❌ ɴᴏ ʙᴀɴɴᴇʀ ғᴏᴜɴᴅ.", processing.chat.id, processing.message_id)
            return
        prime_level = basic.get('prime_info', {}).get('prime_level', 0)
        name = encode_for_url(nickname)
        guild = encode_for_url(clan.get('clan_name', ''))
        pin_id = basic.get('pin_id', '')
        frame = "true" if prime_level >= 8 else "false"
        banner_url = BANNER_API_URL.format(
            headPic=headpic,
            bannerId=banner_id,
            name=name,
            level=basic.get('level', 2),
            guild=guild,
            pinId=pin_id,
            celebrity=basic.get('celebrity_status', 0),
            frame=frame
        )
        img = download_image(banner_url)
        bot.delete_message(processing.chat.id, processing.message_id)
        if img:
            bot.send_photo(message.chat.id, img, caption=f"🎨 ʙᴀɴɴᴇʀ\n👤 {escape(nickname)}\n🔰 @bselius", parse_mode="HTML")
        else:
            bot.reply_to(message, "❌ ғᴀɪʟᴇᴅ.")
    except Exception as e:
        bot.reply_to(message, f"❌ ᴇʀʀᴏʀ: {str(e)}")

@bot.message_handler(commands=['outfit'])
def outfit_command(message):
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "Usage: /outfit <uid>")
            return
        uid = parts[1]
        if not is_valid_uid(uid):
            bot.reply_to(message, "❌ ɪɴᴠᴀʟɪᴅ ᴜɪᴅ.")
            return
        processing = bot.reply_to(message, "🔍 ғᴇᴛᴄʜɪɴɢ ᴏᴜᴛғɪᴛ...")
        data = fetch_player_data_star(uid)
        if not data or 'basic_info' not in data:
            bot.edit_message_text("❌ ᴘʟᴀʏᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ.", processing.chat.id, processing.message_id)
            return
        basic = data['basic_info']
        profile = data.get('profile_info', {})
        nickname = basic.get('nickname', 'ɴ/ᴀ')
        clothes_ids = profile.get('clothes', [])
        avatar_id = profile.get('avatar_id', '')
        if not avatar_id or not clothes_ids:
            bot.edit_message_text("❌ ɴᴏ ᴏᴜᴛғɪᴛ.", processing.chat.id, processing.message_id)
            return
        outfit_url = OUTFIT_API_URL.format(
            avatar_id=avatar_id,
            clothes=','.join(str(c) for c in clothes_ids)
        )
        img = download_image(outfit_url)
        bot.delete_message(processing.chat.id, processing.message_id)
        if img:
            bot.send_photo(message.chat.id, img, caption=f"👕 ᴏᴜᴛғɪᴛ\n👤 {escape(nickname)}\n🔰 @bselius", parse_mode="HTML")
        else:
            bot.reply_to(message, "❌ ғᴀɪʟᴇᴅ.")
    except Exception as e:
        bot.reply_to(message, f"❌ ᴇʀʀᴏʀ: {str(e)}")

@bot.message_handler(commands=['wishlist'])
def wishlist_command(message):
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "Usage: /wishlist <uid_or_name>")
            return
        param = parts[1]
        processing = bot.reply_to(message, "🔍 ғᴇᴛᴄʜɪɴɢ ᴡɪsʜʟɪsᴛ...")
        data = fetch_wishlist(param)
        if not data:
            bot.edit_message_text("❌ ᴘʟᴀʏᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ.", processing.chat.id, processing.message_id)
            return
        player = data.get('player', {})
        wishlist = data.get('wishlist', [])
        wishlist_str = ', '.join(str(item) for item in wishlist) if wishlist else 'ᴇᴍᴘᴛʏ'
        text = f"""📋 ᴡɪsʜʟɪsᴛ
━━━━━━━━━━━━━━━━━━━━━━
👤 ɴᴀᴍᴇ: <code>{escape(player.get('name', 'ɴ/ᴀ'))}</code>
🆔 ᴜɪᴅ: <code>{player.get('uid', 'ɴ/ᴀ')}</code>
🌍 ʀᴇɢɪᴏɴ: <code>{player.get('region', 'ɴ/ᴀ')}</code>
🎁 ɪᴛᴇᴍs: <code>{wishlist_str}</code>
━━━━━━━━━━━━━━━━━━━━━━
🔰 @bselius"""
        bot.delete_message(processing.chat.id, processing.message_id)
        bot.send_message(message.chat.id, text, parse_mode="HTML")
    except Exception as e:
        bot.reply_to(message, f"❌ ᴇʀʀᴏʀ: {str(e)}")

@bot.message_handler(commands=['region'])
def region_command(message):
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "Usage: /region <uid_or_name>")
            return
        param = parts[1]
        processing = bot.reply_to(message, "🔍 ғᴇᴛᴄʜɪɴɢ ʀᴇɢɪᴏɴ...")
        data = fetch_player_data_star(param) if param.isdigit() else None
        if not data or 'basic_info' not in data:
            bot.edit_message_text("❌ ᴘʟᴀʏᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ.", processing.chat.id, processing.message_id)
            return
        basic = data['basic_info']
        text = f"""🌍 ʀᴇɢɪᴏɴ
━━━━━━━━━━━━━━━━━━━━━━
👤 {escape(basic.get('nickname', 'ɴ/ᴀ'))}
🆔 {basic.get('account_id', 'ɴ/ᴀ')}
🌍 ʀᴇɢɪᴏɴ: {basic.get('region', 'ɴ/ᴀ')}
━━━━━━━━━━━━━━━━━━━━━━
🔰 @bselius"""
        bot.delete_message(processing.chat.id, processing.message_id)
        bot.send_message(message.chat.id, text, parse_mode="HTML")
    except Exception as e:
        bot.reply_to(message, f"❌ ᴇʀʀᴏʀ: {str(e)}")

@bot.message_handler(commands=['isbanned', 'bancheck'])
def bancheck_command(message):
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "Usage: /isbanned <uid_or_name>")
            return
        param = parts[1]
        processing = bot.reply_to(message, "🔍 ᴄʜᴇᴄᴋɪɴɢ...")
        data = fetch_bancheck(param)
        if not data:
            bot.edit_message_text("❌ ᴘʟᴀʏᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ.", processing.chat.id, processing.message_id)
            return
        status = "✅ ɴᴏᴛ ʙᴀɴɴᴇᴅ" if data.get('banned') is False else "❌ ʙᴀɴɴᴇᴅ" if data.get('banned') is True else "ᴜɴᴋɴᴏᴡɴ"
        text = f"""🔍 ʙᴀɴ ᴄʜᴇᴄᴋ
━━━━━━━━━━━━━━━━━━━━━━
👤 {escape(data.get('name', 'ɴ/ᴀ'))}
🆔 {data.get('accountId', 'ɴ/ᴀ')}
🌍 {data.get('region', 'ɴ/ᴀ')}
🔒 {status}
━━━━━━━━━━━━━━━━━━━━━━
🔰 @bselius"""
        bot.delete_message(processing.chat.id, processing.message_id)
        bot.send_message(message.chat.id, text, parse_mode="HTML")
    except Exception as e:
        bot.reply_to(message, f"❌ ᴇʀʀᴏʀ: {str(e)}")

@bot.message_handler(commands=['access'])
def access_command(message):
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "Usage: /access <access_token>")
            return
        token = parts[1]
        processing = bot.reply_to(message, "🔄 ᴄᴏɴᴠᴇʀᴛɪɴɢ...")
        result = generate_jwt_from_access(token)
        if not result:
            bot.edit_message_text("❌ ғᴀɪʟᴇᴅ.", processing.chat.id, processing.message_id)
            return
        token_info = f"""┌ ᴛᴏᴋᴇɴ ɪɴғᴏʀᴍᴀᴛɪᴏɴ
├─ ᴀᴄᴄᴏᴜɴᴛ ɪᴅ: <code>{result.get('accountId', 'ɴ/ᴀ')}</code>
├─ ᴀɢᴏʀᴀ ᴇɴᴠ: <code>{result.get('agoraEnvironment', 'ɴ/ᴀ')}</code>
├─ ᴄʀᴇᴀᴛᴇ ᴛɪᴍᴇ: <code>{result.get('create_time', 'ɴ/ᴀ')}</code>
├─ ᴇxᴘɪʀᴇs ɪɴ: <code>{result.get('expires_in', 'ɴ/ᴀ')}</code>
├─ ᴇxᴘɪʀʏ ᴛɪᴍᴇ: <code>{result.get('expiry_time', 'ɴ/ᴀ')}</code>
├─ ɪᴘ ʀᴇɢɪᴏɴ: <code>{result.get('ipRegion', 'ɴ/ᴀ')}</code>
├─ ʟᴏᴄᴋ ʀᴇɢɪᴏɴ: <code>{result.get('lockRegion', 'ɴ/ᴀ')}</code>
├─ ɴᴏᴛɪ ʀᴇɢɪᴏɴ: <code>{result.get('notiRegion', 'ɴ/ᴀ')}</code>
├─ ᴍᴀɪɴ ᴘʟᴀᴛғᴏʀᴍ: <code>{result.get('main_active_platform', 'ɴ/ᴀ')}</code>
├─ ᴘʟᴀᴛғᴏʀᴍ: <code>{result.get('platform', 'ɴ/ᴀ')}</code>
├─ ʀᴇғʀᴇsʜ ᴇxᴘɪʀʏ: <code>{result.get('refresh_expiry_time', 'ɴ/ᴀ')}</code>
├─ sᴄᴏᴘᴇ: <code>{', '.join(result.get('scope', [])) if result.get('scope') else 'ɴ/ᴀ'}</code>
├─ sᴇʀᴠᴇʀ: <code>{result.get('serverUrl', 'ɴ/ᴀ')}</code>
├─ ᴛᴏᴋᴇɴ ᴛʏᴘᴇ: <code>{result.get('token_type', 'ɴ/ᴀ')}</code>
├─ ᴛᴛʟ: <code>{result.get('ttl', 'ɴ/ᴀ')}</code>
├─ ᴅᴀᴛᴀ ᴜɪᴅ: <code>{result.get('uid', 'ɴ/ᴀ')}</code>
├─ ᴏᴘᴇɴ ɪᴅ: <code>{result.get('open_id', 'ɴ/ᴀ')}</code>
├─ ʀᴇғʀᴇsʜ ᴛᴏᴋᴇɴ: <code>{result.get('refresh_token', 'ɴ/ᴀ')}</code>
├─ ᴛᴏᴋᴇɴ: <code>{result.get('token', 'ɴ/ᴀ')}</code>
└─ ᴀᴄᴄᴇss ᴛᴏᴋᴇɴ: <code>{result.get('access_token', 'ɴ/ᴀ')}</code>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔰 ᴄʀᴇᴅɪᴛ: @bselius"""
        bot.delete_message(processing.chat.id, processing.message_id)
        bot.send_message(message.chat.id, token_info, parse_mode="HTML")
    except Exception as e:
        bot.reply_to(message, f"❌ ᴇʀʀᴏʀ: {str(e)}")

@bot.message_handler(commands=['eat'])
def eat_command(message):
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "Usage: /eat <eat_token>")
            return
        eat_token = parts[1]
        processing = bot.reply_to(message, "🔄 ᴄᴏɴᴠᴇʀᴛɪɴɢ EAT...")
        result = generate_jwt_from_eat(eat_token)
        if not result:
            bot.edit_message_text("❌ ғᴀɪʟᴇᴅ.", processing.chat.id, processing.message_id)
            return
        token_info = f"""┌ ᴛᴏᴋᴇɴ ɪɴғᴏʀᴍᴀᴛɪᴏɴ (EAT → JWT)
├─ ᴀᴄᴄᴏᴜɴᴛ ɪᴅ: <code>{result.get('accountId', 'ɴ/ᴀ')}</code>
├─ ɪᴘ ʀᴇɢɪᴏɴ: <code>{result.get('ipRegion', 'ɴ/ᴀ')}</code>
├─ ʟᴏᴄᴋ ʀᴇɢɪᴏɴ: <code>{result.get('lockRegion', 'ɴ/ᴀ')}</code>
├─ ᴛᴏᴋᴇɴ ᴛʏᴘᴇ: <code>{result.get('token_type', 'ɴ/ᴀ')}</code>
├─ ᴅᴀᴛᴀ ᴜɪᴅ: <code>{result.get('uid', 'ɴ/ᴀ')}</code>
├─ ᴏᴘᴇɴ ɪᴅ: <code>{result.get('open_id', 'ɴ/ᴀ')}</code>
├─ ᴛᴏᴋᴇɴ: <code>{result.get('token', 'ɴ/ᴀ')}</code>
└─ ᴀᴄᴄᴇss ᴛᴏᴋᴇɴ: <code>{result.get('access_token', 'ɴ/ᴀ')}</code>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔰 ᴄʀᴇᴅɪᴛ: @bselius"""
        bot.delete_message(processing.chat.id, processing.message_id)
        bot.send_message(message.chat.id, token_info, parse_mode="HTML")
    except Exception as e:
        bot.reply_to(message, f"❌ ᴇʀʀᴏʀ: {str(e)}")

@bot.message_handler(commands=['guild'])
def guild_command(message):
    try:
        parts = message.text.split()
        if len(parts) < 3:
            bot.reply_to(message, "Usage: /guild <clan_id> <region>")
            return
        clan_id = parts[1]
        region = parts[2].upper()
        if not clan_id.isdigit():
            bot.reply_to(message, "❌ ɪɴᴠᴀʟɪᴅ ᴄʟᴀɴ ɪᴅ.")
            return
        processing = bot.reply_to(message, "🔍 ғᴇᴛᴄʜɪɴɢ ɢᴜɪʟᴅ...")
        data = fetch_guild_info(clan_id, region)
        if not data or data.get('status') != 'success':
            bot.edit_message_text("❌ ɢᴜɪʟᴅ ɴᴏᴛ ғᴏᴜɴᴅ.", processing.chat.id, processing.message_id)
            return
        text = f"""🏰 ɢᴜɪʟᴅ ɪɴғᴏʀᴍᴀᴛɪᴏɴ
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🆔 ɢᴜɪʟᴅ ɪᴅ: <code>{data.get('clan_id')}</code>
🏷️ ɴᴀᴍᴇ: <code>{escape(data.get('clan_name', {}).get('414852751800458050', 'ɴ/ᴀ'))}</code>
🌍 ʀᴇɢɪᴏɴ: <code>{data.get('region')}</code>
📊 ʟᴇᴠᴇʟ: <code>{data.get('level')}</code>
⭐ ɢʟᴏʀʏ ᴘᴏɪɴᴛs: <code>{data.get('glory_points')}</code>
👥 ᴍᴇᴍʙᴇʀs: <code>{data.get('current_members')} / {data.get('total_members')}</code>
🟢 ᴏɴʟɪɴᴇ: <code>{data.get('members_online')}</code>
👑 ᴏᴡɴᴇʀ ɪᴅ: <code>{data.get('guild_owner_id')}</code>
📝 ʙɪᴏ: <code>{escape(data.get('guild_bio', 'ɴ/ᴀ'))}</code>
🏅 ʀᴀɴᴋ: <code>{data.get('rank')}</code>
📅 ᴄʀᴇᴀᴛᴇᴅ: <code>{data.get('created_at')}</code>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔰 @bselius"""
        bot.delete_message(processing.chat.id, processing.message_id)
        bot.send_message(message.chat.id, text, parse_mode="HTML")
    except Exception as e:
        bot.reply_to(message, f"❌ ᴇʀʀᴏʀ: {str(e)}")

@bot.message_handler(commands=['bio', 'update_bio'])
def bio_command(message):
    try:
        parts = message.text.split(maxsplit=3)
        if len(parts) < 4:
            bot.reply_to(message, "Usage: /bio <bio> <uid> <password>\nOr: /bio <bio> jwt:<jwt> / access:<access>")
            return
        bio = parts[1]
        param1 = parts[2]
        param2 = parts[3]
        processing = bot.reply_to(message, "🔄 ᴜᴘᴅᴀᴛɪɴɢ ʙɪᴏ...")
        result = None
        if param1.lower().startswith('jwt:'):
            jwt = param1[4:]
            result = upload_bio(bio, jwt=jwt)
        elif param1.lower().startswith('access:'):
            access = param1[7:]
            result = upload_bio(bio, access=access)
        else:
            uid = param1
            password = param2
            if not is_valid_uid(uid):
                bot.edit_message_text("❌ ɪɴᴠᴀʟɪᴅ ᴜɪᴅ.", processing.chat.id, processing.message_id)
                return
            result = upload_bio(bio, uid=uid, password=password)
        if not result or result.get('status') != '✅ Success':
            bot.edit_message_text("❌ ʙɪᴏ ᴜᴘᴅᴀᴛᴇ ғᴀɪʟᴇᴅ.", processing.chat.id, processing.message_id)
            return
        text = f"""✅ ʙɪᴏ ᴜᴘᴅᴀᴛᴇᴅ
━━━━━━━━━━━━━━━━━━━━━━
📝 ɴᴇᴡ ʙɪᴏ: <code>{escape(bio)}</code>
👤 ɴᴀᴍᴇ: <code>{escape(result.get('name', 'ɴ/ᴀ'))}</code>
🆔 ᴜɪᴅ: <code>{result.get('uid', 'ɴ/ᴀ')}</code>
🌍 ʀᴇɢɪᴏɴ: <code>{result.get('region_detected', 'ɴ/ᴀ')}</code>
━━━━━━━━━━━━━━━━━━━━━━
🔰 @bselius"""
        bot.delete_message(processing.chat.id, processing.message_id)
        bot.send_message(message.chat.id, text, parse_mode="HTML")
    except Exception as e:
        bot.reply_to(message, f"❌ ᴇʀʀᴏʀ: {str(e)}")

# ============ WITHOUT SLASH SUPPORT ============

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    """Handle text messages without slash (dual command support)"""
    try:
        text = message.text.strip()
        
        # Check for Get command (without slash)
        if text.lower().startswith('get '):
            parts = text.split()
            if len(parts) >= 2:
                uid = parts[1]
                if is_valid_uid(uid):
                    msg = message
                    msg.text = f"/info {uid}"
                    info_command(msg)
                return
        
        # Check for Level command (without slash)
        if text.lower().startswith('level '):
            parts = text.split()
            if len(parts) >= 3:
                uid = parts[1]
                password = parts[2]
                if is_valid_uid(uid):
                    msg = message
                    msg.text = f"/level {uid} {password}"
                    level_command(msg)
                return
        
        # Check for Token command (without slash)
        if text.lower().startswith('token '):
            parts = text.split()
            if len(parts) >= 3:
                uid = parts[1]
                password = parts[2]
                if is_valid_uid(uid):
                    msg = message
                    msg.text = f"/token {uid} {password}"
                    token_command(msg)
                return
        
        # Check for Access command (without slash)
        if text.lower().startswith('access '):
            parts = text.split()
            if len(parts) >= 2:
                token = parts[1]
                msg = message
                msg.text = f"/access {token}"
                access_command(msg)
                return
        
        # Check for Eat command (without slash)
        if text.lower().startswith('eat '):
            parts = text.split()
            if len(parts) >= 2:
                eat_token = parts[1]
                msg = message
                msg.text = f"/eat {eat_token}"
                eat_command(msg)
                return
        
        # Check for Banner command (without slash)
        if text.lower().startswith('banner '):
            parts = text.split()
            if len(parts) >= 2:
                uid = parts[1]
                if is_valid_uid(uid):
                    msg = message
                    msg.text = f"/banner {uid}"
                    banner_command(msg)
                return
        
        # Check for Outfit command (without slash)
        if text.lower().startswith('outfit '):
            parts = text.split()
            if len(parts) >= 2:
                uid = parts[1]
                if is_valid_uid(uid):
                    msg = message
                    msg.text = f"/outfit {uid}"
                    outfit_command(msg)
                return
        
        # Check for Wishlist command (without slash)
        if text.lower().startswith('wishlist '):
            parts = text.split()
            if len(parts) >= 2:
                param = parts[1]
                msg = message
                msg.text = f"/wishlist {param}"
                wishlist_command(msg)
                return
        
        # Check for Isbanned command (without slash)
        if text.lower().startswith('isbanned ') or text.lower().startswith('bancheck '):
            parts = text.split()
            if len(parts) >= 2:
                param = parts[1]
                msg = message
                msg.text = f"/isbanned {param}"
                bancheck_command(msg)
                return
        
        # Check for Region command (without slash)
        if text.lower().startswith('region '):
            parts = text.split()
            if len(parts) >= 2:
                param = parts[1]
                msg = message
                msg.text = f"/region {param}"
                region_command(msg)
                return
        
        # Check for Icon command (without slash)
        if text.lower().startswith('icon '):
            parts = text.split()
            if len(parts) >= 2:
                icon_id = parts[1]
                if icon_id.isdigit():
                    msg = message
                    msg.text = f"/icon {icon_id}"
                    icon_command(msg)
                return
        
        # Check for Item command (without slash)
        if text.lower().startswith('item '):
            parts = text.split()
            if len(parts) >= 2:
                item_id = parts[1]
                if item_id.isdigit():
                    msg = message
                    msg.text = f"/item {item_id}"
                    item_command(msg)
                return
        
        # Check for Guild command (without slash)
        if text.lower().startswith('guild '):
            parts = text.split()
            if len(parts) >= 3:
                clan_id = parts[1]
                region = parts[2]
                if clan_id.isdigit():
                    msg = message
                    msg.text = f"/guild {clan_id} {region}"
                    guild_command(msg)
                return
        
        # Check for Bio command (without slash)
        if text.lower().startswith('bio ') or text.lower().startswith('update_bio '):
            parts = text.split(maxsplit=3)
            if len(parts) >= 4:
                bio = parts[1]
                param1 = parts[2]
                param2 = parts[3]
                msg = message
                msg.text = f"/bio {bio} {param1} {param2}"
                bio_command(msg)
                return
        
        # If only UID is sent, treat as info
        if is_valid_uid(text):
            uid = text
            msg = message
            msg.text = f"/info {uid}"
            info_command(msg)
            
    except Exception as e:
        bot.reply_to(message, f"❌ ᴇʀʀᴏʀ: {str(e)}")

# ============ START BOT ============
if __name__ == "__main__":
    print("\n" + "="*50)
    print("🤖 Bot Started Successfully!")
    print("="*50)
    print("📡 API Sources:")
    print("  1. Player Info     → STAR_RDP (star-info-api)")
    print("  2. Level Info      → STAR_RDP (guest-info)")
    print("  3. Ban Check       → killersharmabot")
    print("  4. Wishlist        → killersharmabot")
    print("  5. Guild Info      → STAR_RDP")
    print("  6. JWT Token       → STAR_RDP (token.killersharmabot)")
    print("  7. Access to JWT   → STAR_RDP (access.killersharmabot)")
    print("  8. EAT to Access   → Garena Official")
    print("  9. Bio Update      → STAR_RDP")
    print(" 10. Icon PNG        → STAR_RDP (star-icon-png)")
    print(" 11. Outfit Image    → killersharmabot/image")
    print(" 12. Banner Image    → killersharmabot/image")
    print(" 13. Avatar Image    → ffoutfitapis")
    print(" 14. Item API        → item-image-api")
    print("="*50)
    print(f"🔰 Developer: @bselius")
    print(f"📝 Commands: /info, /level, /token, /access, /eat, /icon, /item, /guild, /bancheck, /wishlist, /banner, /outfit, /region, /bio")
    print("📝 Without Slash: get, level, token, access, eat, icon, item, guild, isbanned, wishlist, banner, outfit, region, bio")
    print("="*50 + "\n")
    try:
        bot.polling(none_stop=True, interval=0)
    except Exception as e:
        print(f"❌ Bot error: {e}")