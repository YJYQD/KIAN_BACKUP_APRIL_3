import logging
import sqlite3
import requests
import hashlib
import hmac
import time
import os
import sys
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes, \
    PreCheckoutQueryHandler
from datetime import datetime
from kvsqlite.sync import Client as uu
from dotenv import load_dotenv
from invoice_system import InvoiceSystem

# تحميل المتغيرات من .env

# ==================================================
# إعدادات البوت الأساسية
# ==================================================
load_dotenv()
TOKEN = os.getenv("PAYMENT_BOT_TOKEN_1")
if not TOKEN:
    raise ValueError("TOKEN is missing from .env")

# قائمة المشرفين (مالكَين)
OWNER_ID_1 = int(os.getenv("OWNER_ID", "7284600657"))
OWNER_ID_2 = int(os.getenv("OWNER_ID_2", "94159736"))
OWNER_IDS = [OWNER_ID_1, OWNER_ID_2]  # قائمة المشرفين الاثنين
OWNER_ID = OWNER_ID_1  # للتوافقية مع الكود القديم

# إعدادات Binance
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_SECRET_KEY = os.getenv("BINANCE_SECRET_KEY")
BINANCE_WALLET = os.getenv("BINANCE_WALLET")

# إعداد التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


# ==================================================
# إعداد قاعدة البيانات
# ==================================================
def init_db():
    conn = sqlite3.connect('bot.db', check_same_thread=False)
    cursor = conn.cursor()

    # جدول المستخدمين
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS users
                   (
                       user_id
                       INTEGER
                       PRIMARY
                       KEY,
                       username
                       TEXT,
                       first_name
                       TEXT,
                       balance
                       REAL
                       DEFAULT
                       0.0,
                       total_spent
                       REAL
                       DEFAULT
                       0.0,
                       orders_count
                       INTEGER
                       DEFAULT
                       0,
                       joined_at
                       TIMESTAMP
                       DEFAULT
                       CURRENT_TIMESTAMP
                   )
                   ''')

    # جدول المعاملات
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS transactions
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       user_id
                       INTEGER,
                       amount
                       REAL,
                       txid
                       TEXT,
                       status
                       TEXT
                       DEFAULT
                       'pending',
                       created_at
                       TIMESTAMP
                       DEFAULT
                       CURRENT_TIMESTAMP,
                       FOREIGN
                       KEY
                   (
                       user_id
                   ) REFERENCES users
                   (
                       user_id
                   )
                       )
                   ''')

    conn.commit()
    conn.close()
    print("✅ تم تهيئة قاعدة البيانات")


init_db()

# ربط قاعدة بيانات البوت الرئيسي
main_db = uu('database/main.ss', 'bot')

# تهيئة نظام الفواتير
invoice_system = InvoiceSystem(main_db)


# ==================================================
# دوال قاعدة البيانات
# ==================================================
def get_db_connection():
    return sqlite3.connect('bot.db')


def get_user_balance(user_id):
    """الحصول على رصيد المستخدم من قاعدة البيانات الرئيسية"""
    user_key = f"user_{user_id}"
    if main_db.exists(user_key):
        user_data = main_db.get(user_key)
        return float(user_data.get("coins", 0))
    return 0.0


def update_user_balance(user_id, amount):
    """تحديث رصيد المستخدم"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # التحقق من وجود المستخدم
    cursor.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()

    if result:
        new_balance = result[0] + amount
        new_balance = round(new_balance, 2)
        cursor.execute('UPDATE users SET balance = ? WHERE user_id = ?', (new_balance, user_id))
    else:
        new_balance = round(amount, 2)
        cursor.execute('INSERT INTO users (user_id, balance) VALUES (?, ?)', (user_id, new_balance))

    conn.commit()
    conn.close()
    return new_balance


def save_transaction(user_id, amount, txid, status='pending'):
    """حفظ المعاملة"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
                   INSERT INTO transactions (user_id, amount, txid, status)
                   VALUES (?, ?, ?, ?)
                   ''', (user_id, amount, txid, status))
    conn.commit()
    conn.close()


def update_transaction_status(txid, status):
    """تحديث حالة المعاملة"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE transactions SET status = ? WHERE txid = ?', (status, txid))
    conn.commit()
    conn.close()


# ==================================================
# دوال Binance API
# ==================================================
def get_binance_data(params, endpoint):
    """الحصول على بيانات من Binance API"""
    query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
    signature = hmac.new(
        BINANCE_SECRET_KEY.encode(),
        query_string.encode(),
        hashlib.sha256
    ).hexdigest()

    params['signature'] = signature
    headers = {'X-MBX-APIKEY': BINANCE_API_KEY}

    try:
        response = requests.get(endpoint, params=params, headers=headers, timeout=30)
        return response.json()
    except Exception as e:
        logging.error(f"Binance API error: {e}")
        return None


def verify_binance_payment(txid, amount):
    """التحقق من معاملة Binance"""
    endpoint = 'https://api3.binance.com/sapi/v1/pay/transactions'
    params = {
        'timestamp': int(time.time() * 1000),
        'status': '1',  # المكتملة فقط
        'startTime': (int(time.time()) - 7200) * 1000,  # آخر ساعتين
        'endTime': int(time.time()) * 1000,
        'limit': 100
    }

    data = get_binance_data(params, endpoint)

    if not data or 'data' not in data:
        return False

    for transaction in data['data']:
        if str(transaction.get('orderId')) == str(txid):
            if (transaction.get('currency') == 'USDT' and
                    float(transaction.get('amount', 0)) == float(amount)):
                return True

    return False


# ==================================================
# دوال الملفات المؤقتة
# ==================================================
def save_temp_amount(user_id, amount):
    """حفظ المبلغ مؤقتاً"""
    try:
        os.makedirs('temp', exist_ok=True)
        with open(f"temp/amount_{user_id}.txt", "w") as f:
            f.write(str(amount))
        return True
    except Exception as e:
        logging.error(f"Error saving amount: {e}")
        return False


def get_temp_amount(user_id):
    """قراءة المبلغ المحفوظ"""
    try:
        with open(f"temp/amount_{user_id}.txt", "r") as f:
            return float(f.read().strip())
    except:
        return 0


def cleanup_temp_files(user_id):
    """تنظيف الملفات المؤقتة"""
    try:
        if os.path.exists(f"temp/amount_{user_id}.txt"):
            os.remove(f"temp/amount_{user_id}.txt")
    except:
        pass


def is_txid_used(txid):
    """التحقق إذا كان TXID مستخدم مسبقاً"""
    try:
        if not os.path.exists('temp/used_txids.txt'):
            return False

        with open("temp/used_txids.txt", "r") as f:
            used_txids = [line.strip() for line in f.readlines() if line.strip()]
        return txid in used_txids
    except:
        return False


def mark_txid_used(txid):
    """وضع علامة أن TXID مستخدم"""
    try:
        os.makedirs('temp', exist_ok=True)
        with open("temp/used_txids.txt", "a") as f:
            f.write(txid + "\n")
        return True
    except Exception as e:
        logging.error(f"Error marking TXID used: {e}")
        return False


# ==================================================
# دوال واجهة البوت
# ==================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """بدء استخدام البوت"""
    user_id = update.effective_user.id
    username = update.effective_user.username
    first_name = update.effective_user.first_name

    # تسجيل المستخدم إذا كان جديداً
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM users WHERE user_id = ?', (user_id,))
    if not cursor.fetchone():
        cursor.execute('INSERT INTO users (user_id, username, first_name) VALUES (?, ?, ?)',
                       (user_id, username, first_name))
        conn.commit()
    conn.close()

    message = """
🌟 **مرحباً بك في بوت الشحن التلقائي!**

🤖 **مميزات البوت:**
• شحن رصيد تلقائي عبر Binance
• تحويلات فورية وآمنة
• رصيدك آمن معنا

📊 **إبدأ الآن باستخدام الأزرار أدناه:**
"""

    keyboard = [
        [InlineKeyboardButton(" شحن الرصيد", callback_data="charge_balance")],
        [InlineKeyboardButton("💳 رصيدي", callback_data="my_balance")],
        [InlineKeyboardButton("📊 الإحصائيات", callback_data="stats")],
        [InlineKeyboardButton("@QQ7iBOT", url="https://t.me/QQ7iBOT")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(message, reply_markup=reply_markup)


async def my_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض رصيد المستخدم"""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    balance = get_user_balance(user_id)

    message = f"""
💳︙**رصيدك الحالي:**

**{balance:.2f} (سعودي ﷼)**

📥︙**لشحن رصيدك اضغط على زر شحن الرصيد**
"""

    keyboard = [
        [InlineKeyboardButton(" شحن الرصيد", callback_data="charge_balance")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(message, reply_markup=reply_markup)


async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """القائمة الرئيسية"""
    query = update.callback_query
    await query.answer()

    message = """
🏠 **القائمة الرئيسية**

اختر من الخيارات التالية:
"""

    keyboard = [
        [InlineKeyboardButton(" شحن الرصيد", callback_data="charge_balance")],
        [InlineKeyboardButton("💳 رصيدي", callback_data="my_balance")],
        [InlineKeyboardButton("📊 الإحصائيات", callback_data="stats")],
        [InlineKeyboardButton("@QQ7iBOT", url="https://t.me/QQ7iBOT")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(message, reply_markup=reply_markup)


async def charge_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """قائمة شحن الرصيد"""
    query = update.callback_query
    await query.answer()

    message = """
💰 **طرق الشحن المتاحة:**

**1️⃣ شحن بالنجوم** ⭐
   - دفع سريع وآمن عبر نجوم تيليجرام
   - حزم متعددة من 100 إلى 1000 نجمة

**2️⃣ شحن عبر وكيل الشحن** 💳
   - تحويل بنكي مباشر
   - عملات رقمية (USDT, LTC, TON)

**3️⃣ Binance** 🔗
   - غير متوفر حالياً

اختر طريقة الشحن من الأزرار أدناه:
"""

    keyboard = [
        [InlineKeyboardButton("⭐ شحن بالنجوم", callback_data="charge_via_stars")],
        [InlineKeyboardButton("💳 شحن عبر وكيل الشحن", callback_data="charge_via_owner")],
        [InlineKeyboardButton("🔗 Binance (غير متوفر)", callback_data="charge_via_binance")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(message, reply_markup=reply_markup)


async def charge_via_owner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """الشحن عبر وكيل الشحن"""
    query = update.callback_query
    await query.answer()

    message = """
💳 **شحن عبر وكيل الشحن**

للحصول على رصيد، تواصل مع وكيل الشحن:

📞 **@QQ7iBOT**

سيساعدك في:
• التحويل البنكي
• العملات الرقمية (USDT, LTC, TON)
• طرق دفع أخرى

اضغط على الزر أدناه للتواصل:
"""

    keyboard = [
        [InlineKeyboardButton("📞 @QQ7iBOT", url="https://t.me/QQ7iBOT")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="charge_balance")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(message, reply_markup=reply_markup)


async def charge_via_stars(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """قائمة شحن النجوم"""
    query = update.callback_query
    await query.answer()

    message = """
⭐ **شحن الرصيد عبر النجوم (Telegram Stars)**

اختر الباقة المناسبة لك:
• 100 نجمة = 5 ﷼
• 250 نجمة = 12.5 ﷼
• 500 نجمة = 25 ﷼
• 1000 نجمة = 50 ﷼
• 2000 نجمة = 100 ﷼
• 5000 نجمة = 250 ﷼

👇 **اضغط على الباقة للشراء:**
"""
    keyboard = [
        [InlineKeyboardButton("⭐️ 100 نجمة (5 ﷼)", callback_data="stars_100")],
        [InlineKeyboardButton("⭐️ 250 نجمة (12.5 ﷼)", callback_data="stars_250")],
        [InlineKeyboardButton("⭐️ 500 نجمة (25 ﷼)", callback_data="stars_500")],
        [InlineKeyboardButton("⭐️ 1000 نجمة (50 ﷼)", callback_data="stars_1000")],
        [InlineKeyboardButton("⭐️ 2000 نجمة (100 ﷼)", callback_data="stars_2000")],
        [InlineKeyboardButton("⭐️ 5000 نجمة (250 ﷼)", callback_data="stars_5000")],
        [InlineKeyboardButton("⭐️ مبلغ آخر", callback_data="stars_custom")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="charge_balance")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(message, reply_markup=reply_markup)


async def ask_for_custom_stars(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """طلب مبلغ مخصص من النجوم"""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    context.user_data['waiting_for'] = 'custom_stars_amount'

    message = """
⭐ **مبلغ مخصص**

أرسل عدد النجوم الذي تريد دفعه.
الحد الأدنى: 10 نجوم.

❌ للإلغاء ارسل /cancel
"""
    keyboard = [
        [InlineKeyboardButton("🔙 رجوع", callback_data="charge_via_stars")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(message, reply_markup=reply_markup)


async def process_stars_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """بدء عملية الدفع بالنجوم"""
    query = update.callback_query
    await query.answer()

    stars_amount = int(query.data.split("_")[1])
    # حساب القيمة بالريال: 100 نجمة = 5 ريال
    amount_sar = (stars_amount / 100.0) * 5.0

    title = "شحن رصيد"
    description = f"شحن رصيد بقيمة {amount_sar:.2f} ﷼"
    payload = f"stars_{stars_amount}_{query.from_user.id}"
    currency = "XTR"
    price = stars_amount
    prices = [LabeledPrice("شحن رصيد", price)]

    try:
        await context.bot.send_invoice(
            chat_id=query.from_user.id,
            title=title,
            description=description,
            payload=payload,
            provider_token="",  # فارغ لمدفوعات النجوم
            currency=currency,
            prices=prices
        )
    except Exception as e:
        logging.error(f"Error sending invoice: {e}")
        await query.answer("حدث خطأ في إنشاء الفاتورة", show_alert=True)


async def pre_checkout_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة التحقق المسبق للدفع"""
    query = update.pre_checkout_query
    await query.answer(ok=True)


async def successful_payment_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة الدفع الناجح"""
    message = update.message
    payment = message.successful_payment
    payload = payment.invoice_payload

    if payload.startswith("stars_"):
        parts = payload.split("_")
        stars_amount = int(parts[1])
        user_id = int(parts[2])
        # حساب المبلغ بالريال: 100 نجمة = 5 ريال
        amount_sar = (stars_amount / 100.0) * 5.0

        # تحديث الرصيد في قاعدة البيانات الرئيسية
        try:
            user_key = f"user_{user_id}"
            if main_db.exists(user_key):
                user_data = main_db.get(user_key)
                user_data["coins"] = float(user_data.get("coins", 0)) + amount_sar
                main_db.set(user_key, user_data)
            else:
                main_db.set(user_key, {"coins": amount_sar, "id": user_id, "language": "ar", "currency": "SAR"})

            # تحديث الرصيد المحلي
            update_user_balance(user_id, amount_sar)
            save_transaction(user_id, amount_sar, f"STARS_{message.message_id}", 'completed')

            # إنشاء فاتورة الشحن
            user_obj = message.from_user
            recharge_invoice = invoice_system.create_recharge_invoice(
                user_id=user_id,
                user_info={
                    "first_name": user_obj.first_name or "Unknown",
                    "username": user_obj.username or "Unknown"
                },
                amount=amount_sar,
                method="نجوم تيليجرام",
                transaction_id=f"STARS_{message.message_id}"
            )

            # إرسال الفاتورة للعميل
            invoice_text = invoice_system.get_formatted_recharge_invoice(recharge_invoice)
            await message.reply_text(invoice_text)

            # إشعار المشرفين مع الفاتورة
            admin_notification = invoice_system.get_admin_recharge_notification(recharge_invoice)
            for owner_id in OWNER_IDS:
                try:
                    await context.bot.send_message(owner_id, admin_notification)
                except Exception as e:
                    logging.error(f"Error sending notification to admin {owner_id}: {e}")
        except Exception as e:
            logging.error(f"Error processing stars payment: {e}")


async def charge_via_binance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """خيار Binance - معطل مؤقتاً تحت التطوير"""
    query = update.callback_query
    await query.answer()

    message = "🚫 الخدمة غير متوفرة قريباً\n\nجاري تطوير النظام.\n\n📞 للاستعلام:"

    keyboard = [
        [InlineKeyboardButton("@QQ7iBOT", url="https://t.me/QQ7iBOT")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="charge_balance")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(message, reply_markup=reply_markup)


# ==================================================
# معالج الأزرار
# ==================================================

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دالة الإحصائيات"""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    balance = get_user_balance(user_id)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT total_spent, orders_count FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()

    total_spent = result[0] if result and result[0] else 0.0
    orders_count = result[1] if result and result[1] else 0

    cursor.execute('SELECT amount, status FROM transactions WHERE user_id = ? ORDER BY created_at DESC LIMIT 3',
                   (user_id,))
    transactions = cursor.fetchall()
    conn.close()

    message = f"📊 إحصائيات حسابك\n\n"
    message += f"💰 الرصيد الحالي: {balance:.2f}$\n"
    message += f"💸 إجمالي المصروف: {total_spent:.2f}$\n"
    message += f"🛍️ عدد الطلبات: {orders_count}\n\n"
    message += "📈 آخر المعاملات:\n"

    if transactions:
        for i, (amount, status) in enumerate(transactions, 1):
            icon = "✅" if status == 'completed' else "🔄"
            message += f"{i}. {amount}$ - {icon}\n"
    else:
        message += "📭 لا توجد معاملات سابقة\n"

    keyboard = [[InlineKeyboardButton("🔙 رجوع للقائمة", callback_data="main_menu")]]
    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))


async def process_binance_payment(user_id, txid, context):
    """معالجة دفعة Binance"""
    amount = get_temp_amount(user_id)

    if amount <= 0:
        await context.bot.send_message(user_id, "❌ خطأ في قراءة المبلغ. أعد العملية من البداية.")
        return

    # التحقق من TXID المستخدم مسبقاً
    if is_txid_used(txid):
        await context.bot.send_message(
            user_id,
            "❌ هذا المعرف تم استخدامه مسبقًا.\n"
            "لا يمكن إعادة استخدام نفس المعاملة."
        )
        return

    # إرسال رسالة الانتظار
    processing_msg = await context.bot.send_message(
        user_id,
        "🔍 **جاري التحقق من المعاملة في Binance...**\n"
        "⏳ قد يستغرق هذا بضع ثوانٍ"
    )

    # التحقق من المعاملة
    if verify_binance_payment(txid, amount):
        # حفظ TXID كمستخدم
        mark_txid_used(txid)

        # تحديث رصيد المستخدم
        old_balance = get_user_balance(user_id)
        new_balance = update_user_balance(user_id, amount)

        # حفظ المعاملة
        save_transaction(user_id, amount, txid, 'completed')
        update_transaction_status(txid, 'completed')

        # تحديث رصيد البوت الرئيسي
        try:
            user_key = f"user_{user_id}"
            if main_db.exists(user_key):
                user_data = main_db.get(user_key)
                user_data["coins"] = float(user_data.get("coins", 0)) + float(amount)
                main_db.set(user_key, user_data)
            else:
                # إنشاء مستخدم جديد في البوت الرئيسي
                main_db.set(user_key, {"coins": float(amount), "id": user_id, "language": "ar", "currency": "USD"})
            logging.info(f"✅ تم إضافة {amount}$ لرصيد المستخدم {user_id} في البوت الرئيسي")
        except Exception as e:
            logging.error(f"❌ فشل تحديث رصيد البوت الرئيسي: {e}")

        # حذف رسالة الانتظار
        await context.bot.delete_message(
            chat_id=user_id,
            message_id=processing_msg.message_id
        )

        # إنشاء فاتورة الشحن
        recharge_invoice = None
        try:
            # الحصول على معلومات المستخدم من Telegram
            user_chat = await context.bot.get_chat(user_id)
            recharge_invoice = invoice_system.create_recharge_invoice(
                user_id=user_id,
                user_info={
                    "first_name": user_chat.first_name or "Unknown",
                    "username": user_chat.username or "Unknown"
                },
                amount=float(amount),
                method="Binance USDT",
                transaction_id=txid
            )

            # إرسال الفاتورة للعميل
            invoice_text = invoice_system.get_formatted_recharge_invoice(recharge_invoice)
            await context.bot.send_message(user_id, invoice_text)
        except Exception as e:
            logging.error(f"Error creating invoice: {e}")

        # إرسال رسالة النجاح
        success_message = f"""
✅ **تم شحن رصيدك بنجاح!**

💰 **المبلغ المضاف:** {amount} USDT
✅ **تم إضافة الرصيد إلى حسابك في البوت الرئيسي**
🆔 **رقم المعاملة:** `{txid}`

🎉 **تمت العملية بنجاح!**
"""

        keyboard = [
            [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")],
            [InlineKeyboardButton("💰 شحن مرة أخرى", callback_data="charge_balance")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.send_message(
            user_id,
            success_message,
            reply_markup=reply_markup
        )

        # تنظيف الملفات المؤقتة
        cleanup_temp_files(user_id)

        # إرسال إشعار للمشرفين مع الفاتورة
        if recharge_invoice:
            try:
                admin_notification = invoice_system.get_admin_recharge_notification(recharge_invoice)
                for owner_id in OWNER_IDS:
                    try:
                        await context.bot.send_message(owner_id, admin_notification)
                    except Exception as e:
                        logging.error(f"Error sending notification to admin {owner_id}: {e}")
            except Exception as e:
                logging.error(f"Error sending owner notification: {e}")

    else:
        # حذف رسالة الانتظار
        await context.bot.delete_message(
            chat_id=user_id,
            message_id=processing_msg.message_id
        )

        error_message = f"""
❌ **لم يتم العثور على المعاملة أو البيانات غير مطابقة.**

🔍 **تأكد من:**
1. معرف المعاملة صحيح
2. المبلغ مطابق تماماً ({amount} USDT)
3. العملة هي USDT
4. المعاملة مكتملة
5. انتظر بضع دقائق إذا كانت المعاملة حديثة

🔄 يمكنك إعادة إرسال معرف المعاملة أو /cancel للإلغاء
"""

        await context.bot.send_message(user_id, error_message)
        save_transaction(user_id, amount, txid, 'failed')


# ==================================================
# معالجة الرسائل
# ==================================================
async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة جميع الرسائل النصية"""
    message = update.message
    user_id = message.from_user.id
    text = message.text

    if 'waiting_for' not in context.user_data:
        return

    waiting_for = context.user_data['waiting_for']

    if waiting_for == 'binance_amount':
        if text.lower() == '/cancel':
            context.user_data.pop('waiting_for', None)
            cleanup_temp_files(user_id)
            await message.reply_text("❌ تم إلغاء العملية.")
            await send_main_menu(message, context)
            return

        try:
            amount = float(text)
            if amount < 1:
                await message.reply_text("❌ الحد الأدنى للشحن هو 1$")
                return

            if amount > 1000:
                await message.reply_text("❌ الحد الأقصى للشحن هو 1000$")
                return

            # حفظ المبلغ مؤقتاً
            if save_temp_amount(user_id, amount):
                context.user_data.pop('waiting_for', None)

                wallet_info = f"""
💰 **قم بدفع {amount} USDT بالضبط إلى:**

🔢 **رقم المحفظة:** `{BINANCE_WALLET}`

📝 **قبل الدفع تأكد من:**
1. المبلغ مضبوط ({amount} USDT)
2. الرصيد كافي في Binance
3. العمولة مغطاة

**بعد الدفع اضغط على زر تأكيد الدفع:**
"""

                keyboard = [
                    [InlineKeyboardButton("✅ تأكيد الدفع", callback_data="confirm_binance_payment")],
                    [InlineKeyboardButton("🔙 إلغاء", callback_data="charge_balance")]
                ]

                reply_markup = InlineKeyboardMarkup(keyboard)
                await message.reply_text(wallet_info, reply_markup=reply_markup, parse_mode="Markdown")
            else:
                await message.reply_text("❌ حدث خطأ في حفظ البيانات. أعد المحاولة.")

        except ValueError:
            await message.reply_text("❌ الرجاء إدخال مبلغ صحيح (مثال: 5 أو 10.5)")

    elif waiting_for == 'binance_txid':
        if text.lower() == '/cancel':
            context.user_data.pop('waiting_for', None)
            cleanup_temp_files(user_id)
            await message.reply_text("❌ تم إلغاء العملية.")
            await send_main_menu(message, context)
            return

        txid = text.strip()
        if txid:
            context.user_data.pop('waiting_for', None)
            await process_binance_payment(user_id, txid, context)

    elif waiting_for == 'custom_stars_amount':
        if text.lower() == '/cancel':
            context.user_data.pop('waiting_for', None)
            await message.reply_text("❌ تم إلغاء العملية.")
            await send_main_menu(message, context)
            return

        try:
            stars_amount = int(text)
            if stars_amount < 10:
                await message.reply_text("❌ الحد الأدنى هو 10 نجوم. حاول مرة أخرى.")
                return

            context.user_data.pop('waiting_for', None)

            # حساب القيمة بالريال: 100 نجمة = 5 ريال
            amount_sar = (stars_amount / 100.0) * 5.0

            # إنشاء الفاتورة
            title = "شحن رصيد"
            description = f"شحن رصيد بقيمة {amount_sar:.2f} ﷼"
            payload = f"stars_{stars_amount}_{user_id}"
            currency = "XTR"
            prices = [LabeledPrice("شحن رصيد", stars_amount)]

            await context.bot.send_invoice(
                chat_id=user_id,
                title=title,
                description=description,
                payload=payload,
                provider_token="",
                currency=currency,
                prices=prices
            )
        except ValueError:
            await message.reply_text("❌ الرجاء إدخال عدد صحيح للنجوم.")


async def send_main_menu(message, context):
    """إرسال القائمة الرئيسية"""
    menu_message = """
🏠 **القائمة الرئيسية**

اختر من الخيارات التالية:
"""

    keyboard = [
        [InlineKeyboardButton(" شحن الرصيد", callback_data="charge_balance")],
        [InlineKeyboardButton("💳 رصيدي", callback_data="my_balance")],
        [InlineKeyboardButton("📊 الإحصائيات", callback_data="stats")],
        [InlineKeyboardButton("@QQ7iBOT", url="https://t.me/QQ7iBOT")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await message.reply_text(menu_message, reply_markup=reply_markup)


# ==================================================
# معالج الأزرار
# ==================================================
# معالج الأزرار
# ==================================================

async def confirm_binance_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تأكيد عملية الدفع عبر Binance"""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    context.user_data['waiting_for'] = 'binance_txid'

    message = """
🔍 **تأكيد الدفع**

أرسل معرف العملية (TXID) من Binance

مثال: 123456789

❌ للإلغاء ارسل /cancel
"""
    keyboard = [[InlineKeyboardButton("🔙 إلغاء", callback_data="charge_balance")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(message, reply_markup=reply_markup)
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة جميع أزرار الكيبورد"""
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "charge_balance":
        await charge_balance(update, context)
    elif data == "my_balance":
        await my_balance(update, context)
    elif data == "stats":
       await stats(update, context)
    elif data == "main_menu":
        await main_menu(update, context)
    elif data == "charge_via_binance":
        await charge_via_binance(update, context)
    elif data == "charge_via_owner":
        await charge_via_owner(update, context)
    elif data == "charge_via_stars":
        await charge_via_stars(update, context)
    elif data == "stars_custom":
        await ask_for_custom_stars(update, context)
    elif data.startswith("stars_"):
        await process_stars_payment(update, context)
    elif data == "confirm_binance_payment":
        await confirm_binance_payment(update, context)
    elif data == "admin_users":
        await admin_users(update, context)
    elif data == "admin_transactions":
        await admin_transactions(update, context)
    elif data == "admin_binance":
        await admin_binance(update, context)
    elif data == "admin_back":
        await admin_back(update, context)


# ==================================================
# الأوامر الإدارية
# ==================================================
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """لوحة تحكم المالك"""
    user_id = update.effective_user.id

    if user_id not in OWNER_IDS:
        await update.message.reply_text("❌ ليس لديك صلاحية الوصول لهذه اللوحة.")
        return

    conn = get_db_connection()
    cursor = conn.cursor()

    # إحصائيات البوت
    cursor.execute('SELECT COUNT(*) FROM users')
    total_users = cursor.fetchone()[0]

    cursor.execute('SELECT SUM(balance) FROM users')
    total_balance = cursor.fetchone()[0] or 0.0

    cursor.execute('SELECT SUM(amount) FROM transactions WHERE status = "completed"')
    total_deposits = cursor.fetchone()[0] or 0.0

    conn.close()

    message = f"""
👑 **لوحة تحكم المالك**

📊 **إحصائيات البوت:**
• 👥 إجمالي المستخدمين: {total_users}
• 💰 إجمالي الأرصدة: {total_balance:.2f}$
• 💳 إجمالي الإيداعات: {total_deposits:.2f}$

⚙️ **خيارات الإدارة:**
"""

    keyboard = [
        [InlineKeyboardButton("👥 قائمة المستخدمين", callback_data="admin_users")],
        [InlineKeyboardButton("💳 جميع المعاملات", callback_data="admin_transactions")],
        [InlineKeyboardButton("⚙️ إعدادات Binance", callback_data="admin_binance")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(message, reply_markup=reply_markup)


async def admin_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض قائمة المستخدمين"""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    if user_id not in OWNER_IDS:
        await query.edit_message_text("❌ ليس لديك صلاحية الوصول.")
        return

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT user_id, username, first_name, balance FROM users ORDER BY balance DESC LIMIT 20')
    users = cursor.fetchall()
    conn.close()

    message = "👥 **قائمة أفضل 20 مستخدم:**\n\n"

    if users:
        for i, (uid, uname, fname, bal) in enumerate(users, 1):
            username_display = f"@{uname}" if uname else fname or "Unknown"
            message += f"{i}. {username_display}\n   💰 {bal:.2f} ﷼ | 🆔 `{uid}`\n\n"
    else:
        message += "📭 لا يوجد مستخدمين بعد.\n"

    keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="admin_back")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(message, reply_markup=reply_markup)


async def admin_transactions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض آخر المعاملات"""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    if user_id not in OWNER_IDS:
        await query.edit_message_text("❌ ليس لديك صلاحية الوصول.")
        return

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT t.user_id, t.amount, t.status, t.created_at, u.username 
        FROM transactions t 
        LEFT JOIN users u ON t.user_id = u.user_id 
        ORDER BY t.created_at DESC 
        LIMIT 15
    ''')
    transactions = cursor.fetchall()
    conn.close()

    message = "💳 **آخر 15 معاملة:**\n\n"

    if transactions:
        for uid, amount, status, created, username in transactions:
            status_icon = "✅" if status == "completed" else "🔄" if status == "pending" else "❌"
            username_display = f"@{username}" if username else f"ID: {uid}"
            message += f"{status_icon} {username_display}\n"
            message += f"   💰 {amount:.2f} ﷼ | {created}\n\n"
    else:
        message += "📭 لا توجد معاملات بعد.\n"

    keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="admin_back")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(message, reply_markup=reply_markup)


async def admin_binance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إعدادات Binance"""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    if user_id not in OWNER_IDS:
        await query.edit_message_text("❌ ليس لديك صلاحية الوصول.")
        return

    message = f"""
⚙️ **إعدادات Binance**

🔑 **API Key:** `{BINANCE_API_KEY[:20]}...`
💼 **المحفظة:** `{BINANCE_WALLET}`

📊 **الحالة:** {"✅ متصل" if BINANCE_API_KEY and BINANCE_SECRET_KEY else "❌ غير متصل"}

⚠️ **ملاحظة:** 
لتغيير الإعدادات، قم بتعديل ملف .env
"""

    keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="admin_back")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(message, reply_markup=reply_markup)


async def admin_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """العودة للوحة التحكم"""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    if user_id not in OWNER_IDS:
        await query.edit_message_text("❌ ليس لديك صلاحية الوصول.")
        return

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) FROM users')
    total_users = cursor.fetchone()[0]

    cursor.execute('SELECT SUM(balance) FROM users')
    total_balance = cursor.fetchone()[0] or 0.0

    cursor.execute('SELECT SUM(amount) FROM transactions WHERE status = "completed"')
    total_deposits = cursor.fetchone()[0] or 0.0

    conn.close()

    message = f"""
👑 **لوحة تحكم المالك**

📊 **إحصائيات البوت:**
• 👥 إجمالي المستخدمين: {total_users}
• 💰 إجمالي الأرصدة: {total_balance:.2f} ﷼
• 💳 إجمالي الإيداعات: {total_deposits:.2f} ﷼

⚙️ **خيارات الإدارة:**
"""

    keyboard = [
        [InlineKeyboardButton("👥 قائمة المستخدمين", callback_data="admin_users")],
        [InlineKeyboardButton("💳 جميع المعاملات", callback_data="admin_transactions")],
        [InlineKeyboardButton("⚙️ إعدادات Binance", callback_data="admin_binance")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(message, reply_markup=reply_markup)


# ==================================================
# الدالة الرئيسية
# ==================================================
def main():
    """تشغيل البوت"""
    try:
        application = Application.builder().token(TOKEN).build()

        # إضافة المعالجات
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("admin", admin_panel))
        application.add_handler(CallbackQueryHandler(button_handler))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages))
        application.add_handler(PreCheckoutQueryHandler(pre_checkout_handler))
        application.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_handler))

        print("=" * 50)
        print("🤖 بوت الشحن التلقائي - ᴋʏᴀɴ sɪᴍ_ʙᴏᴛ")
        print(f"🔗 التوكن: {TOKEN}")
        print(f"👑 المشرفين: {OWNER_IDS}")
        print(f"   - المشرف الأول: {OWNER_ID_1}")
        print(f"   - المشرف الثاني: {OWNER_ID_2}")
        print("=" * 50)
        print("✅ بوت الدفع يعمل الآن...")
        print("📞 اضغط Ctrl+C لإيقاف البوت")
        print("=" * 50)

        application.run_polling()
    except KeyboardInterrupt:
        print("\n✅ تم إيقاف بوت الدفع")
        sys.exit(0)
    except Exception as e:
        print(f"⚠️ خطأ في بوت الدفع: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()