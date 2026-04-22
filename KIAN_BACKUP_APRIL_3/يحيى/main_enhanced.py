# -*- coding: utf-8 -*-
import logging
import traceback # تيقن من إضافة هذا السطر لجلب تفاصيل الخطأ

# إعداد اللوجنج بشكل احترافي لمراقبة كل الحركات
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from cryptography.fernet import Fernet

import subprocess
import sys
import threading
import time
import os
import asyncio
from handlers.buy_handler import handle_otp_input, confirm_login, confirm_buy, request_code, cancel_buy
from handlers.numbers_handler import handle_numbers
from telethon import TelegramClient, functions, Button, events
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError, PhoneCodeExpiredError
from telethon.errors.rpcerrorlist import MessageNotModifiedError

from dotenv import load_dotenv
load_dotenv()
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")

try:
    API_ID = int(API_ID)
except (ValueError, TypeError):
    print("❌ API_ID لازم يكون رقم")
    sys.exit(1)

from kvsqlite.sync import Client as uu

# 🧠 قاعدة البيانات
db_main = uu('database/main.ss', 'bot')
db = db_main
import sqlite3
sqlite3.connect("database/main.ss", timeout=30)

db_sections = {
    "normal": uu('database/normal.ss', 'bot'),
    "fake": uu('database/fake.ss', 'bot'),
    "fraud": uu('database/fraud.ss', 'bot'),
    "old_creation": uu('database/old_creation.ss', 'bot'),
}
def get_section_db(section):
    return db_sections.get(section, db_main)


# 🧩 الأنظمة (handlers)
from handlers.admin_handler import handle_admin, get_admin_panel_buttons
from handlers.storage_handler import handle_storage
from handlers.user_handler import handle_user
from handlers.balance_handler import handle_balance
from handlers.misc_handler import handle_navigation
from handlers.transfer_handler import handle_transfer
from handlers.referral_handler import handle_referral
from handlers.settings_handler import handle_settings
ENC_KEY = os.getenv("ENC_KEY")

if not ENC_KEY:
    raise ValueError("❌ ENC_KEY غير موجود في .env")

user_states = {}
otp_clients = {}
otp_data = {}
otp_lock = asyncio.Lock()

# 🧱 أنظمة إضافية
from language_manager import EnhancedLanguageManager
from storage_system import StorageManager
from referral_system import ReferralSystem
from discount_system import setup_discount_system
from invoice_system import InvoiceSystem
from enhanced_buy_system import setup_enhanced_buy_system
from verification_system import setup_verification_system


try:
    from plugins.get_code import get_code, change_password, enable_password
except Exception:
    pass

# 📁 تأكد من وجود مجلد الداتا
# 📁 تأكد من وجود مجلد الداتا
os.makedirs('database/sessions', exist_ok=True)

# ===== الإعدادات الرئيسية =====


# قاموس أعلام الدول
COUNTRY_FLAGS = {
    'مصر': '🇪🇬',
    'السعودية': '🇸🇦',
    'الإمارات': '🇦🇪',
    'الكويت': '🇰🇼',
    'البحرين': '🇧🇭',
    'قطر': '🇶🇦',
    'عُمان': '🇴🇲',
    'الأردن': '🇯🇴',
    'لبنان': '🇱🇧',
    'فلسطين': '🇵🇸',
    'سوريا': '🇸🇾',
    'العراق': '🇮🇶',
    'اليمن': '🇾🇪',
    'المغرب': '🇲🇦',
    'الجزائر': '🇩🇿',
    'تونس': '🇹🇳',
    'ليبيا': '🇱🇾',
    'السودان': '🇸🇩',
    'تركيا': '🇹🇷',
    'إيران': '🇮🇷',
    'باكستان': '🇵🇰',
    'الهند': '🇮🇳',
    'بنغلاديش': '🇧🇩',
    'أفغانستان': '🇦🇫',
    'ماليزيا': '🇲🇾',
    'إندونيسيا': '🇮🇩',
    'الصين': '🇨🇳',
    'روسيا': '🇷🇺',
    'أمريكا': '🇺🇸',
    'بريطانيا': '🇬🇧',
    'فرنسا': '🇫🇷',
    'ألمانيا': '🇩🇪',
    'إيطاليا': '🇮🇹',
    'إسبانيا': '🇪🇸',
    'كندا': '🇨🇦',
    'أستراليا': '🇦🇺',
    'البرازيل': '🇧🇷',
    'الأرجنتين': '🇦🇷',
    'المكسيك': '🇲🇽',
    'اليابان': '🇯🇵',
    'كوريا': '🇰🇷',
    'تايلاند': '🇹🇭',
    'فيتنام': '🇻🇳',
    'الفلبين': '🇵🇭',
    'سنغافورة': '🇸🇬',
    'نيجيريا': '🇳🇬',
    'كينيا': '🇰🇪',
    'جنوب أفريقيا': '🇿🇦',
    'إثيوبيا': '🇪🇹',
}

def get_country_flag(country_name):
    """الحصول على علم الدولة"""
    # إزالة المسافات الزائدة وتوحيد النص
    country_name = country_name.strip()
    return COUNTRY_FLAGS.get(country_name, '🌐')



# Ensure `api_id` is explicitly converted to an integer
if not API_ID or not API_HASH:
    print("❌ تأكد من API_ID و API_HASH في .env")
    sys.exit(1)

# قائمة المشرفين (اثنين)
admins_env = os.getenv("ADMINS", "")
admins_list = []
for x in admins_env.split(","):
    try:
        admins_list.append(int(x.strip()))
    except:
        pass
if not admins_list:
    raise ValueError("⚠️ لازم تضيف ADMINS في ملف .env")
admin = admins_list[0]  # المشرف الأساسي (للتوافقية)
import secrets

def generate_password():
    return secrets.token_hex(8)
token = os.getenv("MAIN_BOT_TOKEN")


if not token or not API_ID or not API_HASH:
    print("❌ خطأ: تأكد من إضافة API_ID و API_HASH و MAIN_BOT_TOKEN في ملف .env")
    sys.exit(1)

# تيقن من تعريف الكائن واستخدامه بصفة أساسية
# تيقن من تعريف الكائن أولاً بصفة مستقلة
# تيقن من تعريف الكائن بصفة مستقلة
client = TelegramClient('BotSession', api_id=int(API_ID), api_hash=API_HASH)
bot = client



cipher = Fernet(ENC_KEY.encode())
async def run_bot_system():
    """الدالة الأساسية لتشغيل البوت بصفة مستقرة"""
    max_retries = 3
    for retry in range(max_retries):
        try:
            print(f"🔄 جاري الاتصال بـ Telegram (محاولة {retry + 1}/{max_retries})...")

            # ✅ يجب استخدام await هنا لأننا داخل دالة async
            if not await client.is_connected():
                await client.connect()

            print("✅ تم الاتصال بنجاح رسميًا!")
            print("🚀 تحقق من بدء تشغيل بوت كيان الآن...")

            # ✅ يجب استخدام await هنا أيضاً لكي يبقى البوت يعمل ولا ينتهي البرنامج
            await client.run_until_disconnected()
            break
        except Exception as err_obj:
            logger.exception(f"Runtime error: {err_obj}")
            if "database is locked" in str(err_obj).lower():
                print(f"⚠️ قاعدة البيانات مغلقة بصفة مؤقتة، سأحاول مجددًا...")
                await asyncio.sleep(5)
                continue

# Ensure `MangSession` is imported at the top

# Explicitly initialize `client` before its usage

# إنشاء قاعدة البيانات
# تهيئة أسعار العملات إذا لم تكن موجودة (الريال السعودي هو العملة الأساسية)
if not db_main.exists("currency_rates"):
    db_main.set("currency_rates", {"SAR": 1.0, "YER": 66.67, "USD": 0.267})
ACCOUNT_TYPE_META = {
    "normal": {
        "title": "شراء رقم",
        "emoji": "📞",
        "db_key": "normal_settings",
        "countries_key": "countries"
    },
    "fake": {
        "title": "ارقام مزيف",
        "emoji": "🎭",
        "db_key": "fake_settings",
        "countries_key": "fake_countries_settings"
    },
    "fraud": {
        "title": "ارقام احتيالي",
        "emoji": "⚠️",
        "db_key": "fraud_settings",
        "countries_key": "fraud_countries_settings"
    },
    "old_creation": {
        "title": "حسابات إنشاء قديمه",
        "emoji": "📱",
        "db_key": "old_creation_settings",
        "countries_key": "old_creation_countries_settings"
    }
}

ACCOUNT_TYPE_LOCKS = {
    "fake": asyncio.Lock(),
    "fraud": asyncio.Lock(),
    "old_creation": asyncio.Lock(),
}
# قفل شراء الأرقام العادية لمنع البيع المكرر وقت الضغط المتزامن.
NORMAL_BUY_LOCK = asyncio.Lock()

def is_admin_user(user_id):
    admins = db.get("admins") if db.exists("admins") else []
    return user_id == admin or user_id in admins


def get_type_country_settings(account_type):
    """إرجاع إعدادات الدول للقسم المحدد فقط دون دمج أو توافق رجعي"""
    if account_type == "normal":
        # الأرقام العادية: قائمة الدول من db الخاص بالقسم
        countries = db_sections["normal"].get("countries") if db_sections["normal"].exists("countries") else []
        settings = {}
        for country in countries:
            name = str(country.get("name", "Unknown"))
            settings[name] = {
                "calling_code": str(country.get("calling_code", "")),
                "price": float(country.get("price", 0))
            }
        return settings
    meta = ACCOUNT_TYPE_META.get(account_type)
    if not meta or not meta.get("countries_key"):
        return {}
    countries_key = meta["countries_key"]
    section_db = db_sections.get(account_type, db_main)
    settings = section_db.get(countries_key) if section_db.exists(countries_key) else {}
    if not isinstance(settings, dict):
        settings = {}
    return settings
def get_type_stock_rows(account_type):
    """إرجاع الدول التي لديها مخزون جاهز للبيع (status: selling)"""
    rows = []

    manager = storage_managers.get(account_type)
    if not manager:
        return rows

    all_nums = manager.get_accounts_by_type(account_type)
    ready_nums = [n for n in all_nums if n.get("status") == "selling"]

    country_stats = {}
    for n in ready_nums:
        c_name = n.get("country", "Unknown")
        country_stats[c_name] = country_stats.get(c_name, 0) + 1

    settings = get_type_country_settings(account_type)

    for name, count in country_stats.items():
        c_set = settings.get(name, {})
        rows.append({
            "country": name,
            "calling_code": c_set.get("calling_code", ""),
            "price": c_set.get("price", 0),
            "count": count
        })

    return sorted(rows, key=lambda x: x.get("country", ""))


def get_type_total(account_type):
    return sum(item.get("count", 0) for item in get_type_stock_rows(account_type))

def start_payment_system():
    """تشغيل نظام الدفع في thread منفصل مع إعادة التشغيل التلقائي"""
    time.sleep(30)  # انتظر 30 ثانية قبل بدء نظام الدفع لتجنب تضارب قاعدة البيانات
    while True:
        try:
            process = subprocess.Popen([sys.executable, "payment.py"])
            process.wait()
            print(f"⚠️ توقف نظام الدفع بـ code: {process.returncode}")

        except Exception as e:
            logger.exception(f"Payment system crashed: {e}")

        print("🔄 إعادة تشغيل نظام الدفع خلال 20 ثانية...")
        time.sleep(20)





# تهيئة الجداول
if not db.exists("accounts"):
    db.set("accounts", [])

if not db.exists("countries"):
    db.set("countries", [])

if not db.exists("bad_guys"):
    db.set("bad_guys", [])

if not db.exists("force"):
    # قناتان إجباريتان: الرسمية والتفعيلات
    db.set("force", ["QQQ_4i", "QQQ_5i"])

if not db.exists("admins"):
    db.set("admins", admins_list)  # تعيين قائمة المشرفين الاثنين

for account_type, meta in ACCOUNT_TYPE_META.items():
    SECTION_ADMINS = {
        "normal": [admin],
        "fake": [],
        "fraud": [],
        "old_creation": []
    }
    if account_type == "normal":
        continue
    if not db.exists(meta["db_key"]):
        db.set(meta["db_key"], {})
    if not db.exists(meta["countries_key"]):
        db.set(meta["countries_key"], {})

lang_manager = EnhancedLanguageManager(db)
storage_managers = {
    section: StorageManager(db_sections[section])
    for section in db_sections
}
referral_system = ReferralSystem(db)
discount_system = setup_discount_system(db)
invoice_system = InvoiceSystem(db)
enhanced_buy_system = setup_enhanced_buy_system(client, db, lang_manager, storage_managers["normal"], discount_system, db_sections, ACCOUNT_TYPE_META)
verification_system = setup_verification_system(db)


def get_formatted_currency(user_id, amount):
    """عرض المبلغ حسب عملة المستخدم مع الاعتماد على SAR كأساس."""
    user_data = db.get(f"user_{user_id}") if db.exists(f"user_{user_id}") else {}
    currency = user_data.get("currency", "SAR")
    rates = db.get("currency_rates") if db.exists("currency_rates") else {"SAR": 1.0, "YER": 66.67, "USD": 0.267}

    if currency == "YER":
        val = float(amount) * rates.get("YER", 66.67)
        return f"{val:,.0f} ﷼ ريال يمني"
    if currency == "USD":
        val = float(amount) * rates.get("USD", 0.267)
        return f"{val:.2f} 💵 $"

    return f"{float(amount):.2f}"



def should_require_force_sub(user_id):
    """تفعيل الاشتراك الإجباري فقط للمستخدمين الجدد."""
    user_key = f"user_{user_id}"
    if not db.exists(user_key):
        # أي مستخدم غير مسجل يُعامل كمستخدم جديد
        return True

    user_data = db.get(user_key)
    return bool(user_data.get("enforce_force_sub", False))


async def validate_force_subscription(user_id):
    """التحقق من الاشتراك الإجباري وإكمال إحالة المعلقين عند النجاح."""
    if not should_require_force_sub(user_id):
        return True, None

    force_channels = db.get("force") if db.exists("force") else []

    # إذا كانت قائمة القنوات فارغة، سمح للمستخدم بالدخول
    if not force_channels:
        return True, None

    failed_channel = None

    try:
        for channel in force_channels:
            failed_channel = channel
            await client(functions.channels.GetParticipantRequest(
                channel=channel,
                participant=user_id
            ))

        pending_referrer = referral_system.get_pending_referral(user_id)
        if pending_referrer:
            reward = referral_system.complete_pending_referral(user_id)
            if reward > 0:
                try:
                    await client.send_message(
                        int(pending_referrer),
                        f"**🎉︙حصلت على مكافأة إحالة بقيمة {reward} ﷼ ريال سعودي!\n\n📥︙لأن المستخدم {user_id} انضم إلى البوت عبر رابط دعوتك وأكمل التحقق والاشتراك في القنوات!**"
                    )
                except Exception as e:
                    print(f"⚠️ خطأ في إرسال المكافأة: {e}")

        return True, None
    except Exception as e:
        print(f"⚠️ خطأ في التحقق من الاشتراك: {e}")
        return False, failed_channel


def get_force_sub_required_message(channel):
    """رسالة الاشتراك الإجباري مع تفاصيل واضحة"""
    # عرض جميع القنوات الإجبارية
    force_channels = db.get("force") if db.exists("force") else []
    channels_text = "\n".join([f"📢 @{ch}" for ch in force_channels])

    return (
        f"**⚠️ عذراً عزيزي - يجب الاشتراك أولاً!**\n\n"
        f"🚀 **يجب عليك الاشتراك في القنوات التالية قبل استخدام البوت:**\n\n"
        f"{channels_text}\n\n"
        f"✨ **المميزات:**\n"
        f"• تحديثات البوت المستمرة\n"
        f"• عروض وخصومات حصرية\n"
        f"• إعلانات مهمة\n"
        f"• إثباتات التسليم المباشرة\n\n"
        f"📝 **الخطوات:**\n"
        f"1️⃣ اشترك في جميع القنوات أعلاه\n"
        f"2️⃣ أرسل: /start\n"
        f"3️⃣ ستتمكن من استخدام البوت\n\n"
        f"✅ بعد الاشتراك، ستحصل على كامل المميزات!"
    )


class SoldHandler:
    def __init__(self, storage_mgr):
        self.storage_mgr = storage_mgr

    async def show_storage_menu(self, event, user_id):
        stats = self.storage_mgr.get_storage_stats()
        msg = (
            "**📦 إدارة التخزين**\n\n"
            f"• الإجمالي: {stats['total']}\n"
            f"• مخزن: {stats['stored']}\n"
            f"• معروض للبيع: {stats['selling']}\n"
            f"• مباع: {stats['sold']}"
        )
        buttons = [
            [Button.inline("📋 عرض الأرقام", data="view_stored_numbers")],
            [Button.inline("⚙️ البيع التلقائي", data="auto_sell_settings")],
            [Button.inline(lang_manager.get_message(user_id, 'BACK_BUTTON'), data="admin_panel")]
        ]
        await event.edit(msg, buttons=buttons)

    async def show_stored_numbers(self, event, user_id, page=0):
        numbers = self.storage_mgr.get_sold_numbers()
        if not numbers:
            await event.edit("**📭 لا توجد أرقام مخزنة حالياً**", buttons=[[Button.inline(lang_manager.get_message(user_id, 'BACK_BUTTON'), data="storage_menu")]])
            return

        per_page = 10
        start = page * per_page
        end = start + per_page
        chunk = numbers[start:end]

        buttons = []
        for item in chunk:
            phone = item.get("phone_number")
            status = item.get("status", "stored")
            buttons.append([Button.inline(f"+{phone} | {status}", data=f"manage_num:{phone}")])

        nav = []
        if page > 0:
            nav.append(Button.inline("⬅️", data=f"storage_page:{page - 1}"))
        if end < len(numbers):
            nav.append(Button.inline("➡️", data=f"storage_page:{page + 1}"))
        if nav:
            buttons.append(nav)

        buttons.append([Button.inline(lang_manager.get_message(user_id, 'BACK_BUTTON'), data="storage_menu")])
        await event.edit("**📦 الأرقام المخزنة**", buttons=buttons)

    async def show_number_management(self, event, user_id, phone_number):
        num = self.storage_mgr.get_number_by_phone(phone_number)
        if not num:
            await event.answer("❌ الرقم غير موجود", alert=True)
            return

        msg = (
            "**📱 إدارة الرقم**\n\n"
            f"• الرقم: `+{phone_number}`\n"
            f"• الحالة: {num.get('status', 'stored')}\n"
            f"• السعر: {num.get('price', 0)}"
        )

        status = num.get("status", "stored")
        sell_btn = Button.inline("➕ إضافة للبيع", data=f"storage_add_sell:{phone_number}")
        if status == "selling":
            sell_btn = Button.inline("➖ إزالة من البيع", data=f"storage_remove_sell:{phone_number}")

        buttons = [
            [Button.inline("📨 الحصول على الكود", data=f"storage_get_code:{phone_number}")],
            [sell_btn],
            [Button.inline("🗑 حذف", data=f"storage_delete:{phone_number}")],
            [Button.inline(lang_manager.get_message(user_id, 'BACK_BUTTON'), data="view_stored_numbers")]
        ]
        await event.edit(msg, parse_mode="markdown", buttons=buttons)


    async def handle_auto_sell_settings(self, event, user_id):
        st = self.storage_mgr.get_auto_sell_status()
        enabled = st.get("enabled", False)
        msg = f"**⚙️ إعدادات البيع التلقائي**\n\nالحالة الحالية: {'✅ مفعل' if enabled else '❌ معطل'}"
        buttons = [
            [Button.inline("✅ تفعيل", data="enable_auto_sell"), Button.inline("❌ تعطيل", data="disable_auto_sell")],
            [Button.inline(lang_manager.get_message(user_id, 'BACK_BUTTON'), data="storage_menu")]
        ]
        await event.edit(msg, buttons=buttons)

    async def handle_delete_number(self, event, user_id, phone_number):
        self.storage_mgr.remove_number(phone_number)
        await event.edit("✅ تم حذف الرقم من التخزين", buttons=[[Button.inline(lang_manager.get_message(user_id, 'BACK_BUTTON'), data="view_stored_numbers")]])


sold_handler = SoldHandler(storage_managers["normal"])


async def show_referral_menu(event, user_id):
    buttons = [
        [Button.inline("🔗 رابط الدعوة", data="show_referral_link")],
        [Button.inline("📊 إحصائياتي", data="show_referral_stats")],
        [Button.inline(lang_manager.get_message(user_id, 'BACK_BUTTON'), data="main")]
    ]
    admins = db.get("admins") if db.exists("admins") else []
    if user_id == admin or user_id in admins:
        buttons.insert(2, [Button.inline("⚙️ تعديل مكافأة الدعوة", data="change_referral_reward")])

    await event.edit("**🎁 نظام الإحالة**\n\nاختر من الخيارات التالية:", buttons=buttons)


async def show_referral_link(event, user_id):
    code = referral_system.get_referral_code(user_id)
    me = await client.get_me()
    link = f"https://t.me/{me.username}?start={code}"
    msg = f"**🔗 رابط دعوتك:**\n\n`{link}`"
    buttons = [
        [Button.url("فتح الرابط", link)],
        [Button.inline(lang_manager.get_message(user_id, 'BACK_BUTTON'), data="referral_system")]
    ]
    await event.edit(msg, buttons=buttons)


async def show_referral_stats(event, user_id):
    stats = referral_system.get_referral_stats(user_id)
    reward = referral_system.get_referral_reward()
    msg = (
        "**📊 إحصائيات الإحالة**\n\n"
        f"• عدد المدعوين: {stats.get('total_referred', 0)}\n"
        f"• إجمالي الأرباح: {stats.get('total_earned', 0):.2f} ﷼\n"
        f"• مكافأة كل دعوة: {reward:.2f} ﷼"
    )
    await event.edit(msg, buttons=[[Button.inline(lang_manager.get_message(user_id, 'BACK_BUTTON'), data="referral_system")]])


async def change_referral_reward(event, user_id):
    async with bot.conversation(event.chat_id, timeout=120) as x:
        await x.send_message("**💰 أرسل قيمة مكافأة الإحالة الجديدة:**")
        val_msg = await x.get_response()
        try:
            reward = float(val_msg.text)
        except Exception:
            await x.send_message("❌ قيمة غير صحيحة")
            return

        referral_system.set_referral_reward(reward)
        await x.send_message(f"✅ تم تحديث مكافأة الإحالة إلى {reward:.2f} ﷼")


@client.on(events.CallbackQuery(pattern="complete_verification"))
async def complete_verification_handler(event):
    user_id = event.chat_id
    verification_system.cleanup_session(user_id)
    await asyncio.sleep(4)  # انتظار ثانيتين
    await event.edit("**✅ تم التحقق بنجاح!**\n\n**أرسل /start لبدء استخدام البوت**")
# ===== OTP FUNCTIONS =====


async def cleanup_otp(user_id):


    client_ = otp_clients.pop(user_id, None)
    otp_data.pop(user_id, None)

    if client_:
        try:
            await client_.disconnect()
        except Exception as e:
            logger.exception(e)

    return True

async def verify_otp(user_id, code):
    data = otp_data.get(user_id)
    client_otp = otp_clients.get(user_id)

    if not data or not client_otp:
        return "no_session"

    try:
        await client_otp.sign_in(
            phone=data["phone"],
            code=code,
            phone_code_hash=data["hash"]
        )

        raw_session = client_otp.session.save()
        encrypted_session = cipher.encrypt(raw_session.encode()).decode()


        phone = data["phone"]

        COUNTRY_PREFIX = {
            "+966": ("السعودية", "966"),
            "+20": ("مصر", "20"),
        }

        country = "Unknown"
        calling_code = ""
        for prefix, c_data in COUNTRY_PREFIX.items():
            if phone.startswith(prefix):
                country, calling_code = c_data
                break

        storage_managers["normal"].add_account("normal", {
            "phone_number": data["phone"],
            "session": encrypted_session,
            "country": "Unknown",
            "calling_code": "",
            "price": 10.0,
            "two_step": os.getenv("DEFAULT_TWO_STEP", "Visco")
        })

        return True

    except PhoneCodeInvalidError:

        return "invalid_code"

    except PhoneCodeExpiredError:
        return "expired_code"

        # --- استبدل الجزء أدناه بالكود الجديد ---
    except SessionPasswordNeededError:
        try:
            otp_clients.pop(user_id, None)
            otp_data.pop(user_id, None)
            session = client_otp.session.save()
            await client_otp.disconnect()
            # محاولة الدخول بكلمة السر الافتراضية من ملف .env
            storage_managers["normal"].add_account("normal", {
                "phone_number": data["phone"],
                "session": session,
                "country": "Unknown",
                "two_step": os.getenv("DEFAULT_TWO_STEP", "Visco")
            })
            return True
        except:
            return "2fa_required"
        # ----------------------------------------


    except Exception as e:

        logger.error(f"OTP Error: {e}")

        return "error"




@client.on(events.NewMessage(func=lambda x: x.is_private and getattr(x, "text", "") and not x.text.startswith('/')))
async def global_message_handler(event):
    user_id = event.chat_id
    text = event.text.strip()
    bad_guys = db.get("bad_guys") if db.exists("bad_guys") else []
    if str(user_id) in bad_guys:
        return  # يتجاهل أي رسالة من المحظور

    # نظام التحقق
    if not verification_system.is_user_verified(user_id):
        success, message = verification_system.verify_answer(user_id, text)

        if success:
            buttons = [[Button.inline("إتمام التحقق ✅", data="complete_verification")]]
            await event.reply(f"**{message}**", buttons=buttons)
        else:
            await event.reply(f"❌ {message}")
        return

    # OTP
    try:
        if await handle_otp_input(event, user_id, text, otp_clients, otp_data):
            return
    except Exception as e:
        logger.exception(f"OTP handler error: {e}")
        return

@client.on(events.NewMessage(pattern="/start"))
async def start(event):
    user_id = event.chat_id
    bans = db.get('bad_guys') if db.exists('bad_guys') else []

    # ===== START HANDLER CLEAN =====



    message_text = event.text if getattr(event, "text", None) else "/start"
    referrer_id = None

    # نظام الإحالة فقط
    if len(message_text.split()) > 1:
        referral_code = message_text.split()[1]
        referrer_id = referral_system.get_user_by_referral_code(referral_code)

        if referrer_id and referrer_id != user_id:
            referral_system.add_pending_referral(referrer_id, user_id)

    # نظام التحقق (مستقل تمامًا)
    if not verification_system.is_user_verified(user_id):
        async with bot.action(user_id, 'typing'):
            await asyncio.sleep(1)

        question = verification_system.create_verification_session(user_id)

        message = (
            "**🛡️ اختبار الذكاء الخارق - ᴋʏᴀɴ sɪᴍ_ʙᴏᴛ**\n\n"
            "يا هلا والله! أثبت لنا إنك انسان وحل هالمعجزة:\n\n"
            f"🔢 **كم ناتج الحسبة: {question} = ؟**\n\n"
            "**⚠️ أرسل الناتج برقم فقط (مثلاً: 5)**"
        )

        await event.reply(message)
        return

    is_subscribed, channel = await validate_force_subscription(user_id)
    if not is_subscribed:
        await event.reply(get_force_sub_required_message(channel))
        return

    if user_id in bans:
        return



    if not db.exists(f"user_{user_id}"):
        members = 0
        db.set(f"user_{user_id}", {
            "coins": 0,
            "id": user_id,
            "language": "ar",
            "currency": "SAR",
            # هذه العلامة تضمن أن الاشتراك الإجباري يطبق على المستخدمين الجدد فقط
            "enforce_force_sub": True
        })

        try:
            user_info = await client.get_entity(user_id)
            users = db.keys('user_%')
            members = len(users)
            username = "None" if user_info.username is None else "@" + str(user_info.username)

            message_text = f'• دَخَلَ شخصٌ جديدٌ إلى البوت الخاص بك 👾\n\n- معلوماتُ المستخدمِ الجديدِ.\n\n- اسمُهُ: <a href="tg://user?id={user_id}">{user_info.first_name}</a>\n- معرفُهُ: {username}\n- آيديه: {user_id}\n\n• إجمالي الأعضاء: {members}'

            for admin_id in admins_list:
                try:
                    await bot.send_message(admin_id, message_text, parse_mode="html")
                except Exception as e:
                    print(f"❌ خطأ في إرسال الرسالة للأدمن {admin_id}: {e}")
        except Exception as e:
            print(f"❌ خطأ في جلب معلومات المستخدم: {e}")


    user_data = db.get(f"user_{user_id}")
    if "currency" not in user_data:
        user_data["currency"] = "SAR"
        db.set(f"user_{user_id}", user_data)

    # تحديث اليوزرنيم بشكل دوري ليظهر في شاشة عرض المستخدمين
    try:
        sender = await event.get_sender()
        latest_username = sender.username if sender and sender.username else ""
    except Exception:
        latest_username = user_data.get("username", "")

    if user_data.get("username", "") != latest_username:
        user_data["username"] = latest_username
        db.set(f"user_{user_id}", user_data)

    coins = db.get(f"user_{user_id}")["coins"]
    formatted_coins = get_formatted_currency(user_id, coins)

    admins = db.get("admins") if db.exists("admins") else []
    if user_id == admin or user_id in admins:
        keyboard = get_admin_panel_buttons(user_id)
        await event.reply(lang_manager.get_message(user_id, 'ADMIN_MESSAGE'), buttons=keyboard)

        await asyncio.sleep(1)

        await event.reply(lang_manager.get_message(user_id, 'START_MESSAGE', user_id, formatted_coins),
                          buttons=lang_manager.get_main_buttons(user_id))
    else:
        await event.reply(lang_manager.get_message(user_id, 'START_MESSAGE', user_id, formatted_coins),
                          buttons=lang_manager.get_main_buttons(user_id))

# --- 1. دالة العرض (يجب أن تبدأ من حافة السطر تماماً) ---
# --- 1. دالة العرض (تم تصحيح الإزاحة) ---
async def render_main_menu(event):
    user_id = event.chat_id
    coins = (db.get(f"user_{user_id}") or {"coins": 0}).get("coins", 0)
    formatted_coins = get_formatted_currency(user_id, coins)
    try:
        await event.edit(
            lang_manager.get_message(user_id, 'START_MESSAGE', user_id, formatted_coins),
            buttons=lang_manager.get_main_buttons(user_id)
        )
    except MessageNotModifiedError:
        pass

@client.on(events.CallbackQuery())
async def callback_handler(event):
    u_id_val = event.chat_id
    if not event.data: return
    data = event.data.decode("utf-8")

    # 🛑 إضافة هذا السطر لحل مشكلة "تحت الصيانة" في أزرار الشراء
    if data.startswith("enhanced_"):
        await enhanced_buy_system.handle_callback(event, data, u_id_val)
        return

    pk = f"purchase_{u_id_val}"
    active_purchase = enhanced_buy_system.active_purchases.get(pk, {})
    current_cat = active_purchase.get('category', 'normal')
    manager = storage_managers.get(current_cat, storage_managers["normal"])

    # 1. إيقاف علامة التحميل (الساعة) فور الضغط على أي زر
    await event.answer()

    # 2. تجهيز السياق (Context) الموحد لجميع الهاندلرات
    ctx = {
        "api_id": API_ID, "api_hash": API_HASH, "db": db,
        "lang_manager": lang_manager, "get_formatted_currency": get_formatted_currency,
        "enhanced_buy_system": enhanced_buy_system, "cb_answer": event.answer,
        "storage_manager": manager,
        "storage_managers": storage_managers,
        "send_otp": send_otp, "verify_otp": verify_otp,
        "referral_system": referral_system, "discount_system": discount_system,
        "invoice_system": invoice_system,  # أضفناه لكي تعمل إحصائيات المبيعات في الأدمن
        "render_main_menu": render_main_menu,
    }

    # 3. معالجة أزرار نظام الشراء الأساسي (Confirm/Cancel)
    if data == "confirm_buy": await confirm_buy(event, u_id_val, manager, db); return
    if data == "request_code": await request_code(event, u_id_val); return
    if data == "confirm_login": await confirm_login(event, u_id_val, manager, db); return
    if data == "cancel_buy": await cancel_buy(event, u_id_val); return

    # 4. أزرار اختيار الأقسام (عادي، مزيف، إلخ)
    if data.startswith("buy_cat_"):
        category = data.replace("buy_cat_", "")
        if pk not in enhanced_buy_system.active_purchases:
            enhanced_buy_system.active_purchases[pk] = {}
        enhanced_buy_system.active_purchases[pk]['category'] = category
        await enhanced_buy_system.show_countries_menu(event, u_id_val)
        return

    # 5. توزيع المهام على الـ Handlers (ترتيب موحد: event ثم u_id_val ثم data)
    # ملاحظة: الترتيب (event, u_id_val, data) هو المعتمد الآن في كل الملفات
    if await handle_admin(event, u_id_val, data, **ctx): return
    if await handle_numbers(event, u_id_val, data): return
    if await handle_balance(event, u_id_val, data, db): return
    if await handle_storage(event, u_id_val, data, **ctx): return

    # تصحيح ترتيب هذه الاستدعاءات لضمان عمل التحويل والإحالة
    if await handle_user(event, u_id_val, data, **ctx): return
    if await handle_transfer(event, u_id_val, data, **ctx): return
    if await handle_referral(event, u_id_val, data, **ctx): return

    # هاندلر الإعدادات مع وسائطه الخاصة
    if await handle_settings(event, u_id_val, data, lang_manager=lang_manager, db=db, cb_answer=event.answer,
                             render_main_menu=render_main_menu): return

    # الملاحة العامة (مثل كود الخصم وغيرها)
    if await handle_navigation(event, data, u_id_val, **ctx): return
    # ضمان عمل زر الرجوع في كل الظروف
    if data == "main":
        await render_main_menu(event)
        return
    # هذا السطر يظهر فقط للأزرار التي لم يتم تعريفها أعلاه
    await event.answer("⚠️ الزر تحت الصيانة حاليًا.", alert=True)
if __name__ == "__main__":
    try:
        print("⚙️ جاري تحضير الأنظمة الجانبية...")

        async def main():
            # تشغيل نظام الدفع في الخلفية
            threading.Thread(target=start_payment_system, daemon=True).start()

            # تشغيل البوت
            await run_bot_system()

        asyncio.run(main())

    except KeyboardInterrupt:
        print("\n🛑 تم إيقاف البوت بصفة ودية.")
    except Exception as err_obj:
        print(f"⚠️ تحقق من وجود خطأ أثناء تشغيل النظام: {err_obj}")