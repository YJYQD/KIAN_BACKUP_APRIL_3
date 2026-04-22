import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice
import json
import os
import threading
import time
import datetime
import requests
import hmac
import hashlib
from dotenv import load_dotenv

# تحميل المتغيرات من .env
load_dotenv()

# إعدادات Binance
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_SECRET_KEY = os.getenv("BINANCE_SECRET_KEY")
BINANCE_WALLET = os.getenv("BINANCE_WALLET")


class TelegramStarsPaymentSystem:
    def __init__(self, bot_token, admin_id, db, main_bot_username=None):
        self.bot = telebot.TeleBot(bot_token, threaded=False)
        self.admin_id = admin_id
        self.db = db
        self.main_bot_username = main_bot_username

        # قائمة المشرفين (المشرف الأول والمشرف الثاني)
        self.admins_list = [7284600657, 94159736]

        # أسعار التحويل (100 نجمة = 1$)
        self.star_to_dollar_rate = 100

        # تهيئة ملفات البيانات
        self.payment_data_file = "payment_data.json"
        self.load_payment_data()

        # تسجيل معالجات الدفع
        self.register_handlers()

    def load_payment_data(self):
        """تحميل بيانات الدفع"""
        if os.path.exists(self.payment_data_file):
            try:
                with open(self.payment_data_file, 'r', encoding='utf-8') as f:
                    self.payment_data = json.load(f)
            except:
                self.payment_data = {}
        else:
            self.payment_data = {}

    def save_payment_data(self):
        """حفظ بيانات الدفع"""
        with open(self.payment_data_file, 'w', encoding='utf-8') as f:
            json.dump(self.payment_data, f, ensure_ascii=False, indent=4)

    def register_handlers(self):
        """تسجيل معالجات الدفع"""

        @self.bot.callback_query_handler(func=lambda call: call.data == "recharge_with_stars")
        def handle_recharge_with_stars(call):
            self.show_star_packages(call)

        @self.bot.callback_query_handler(func=lambda call: call.data == "recharge_with_binance")
        def handle_recharge_with_binance(call):
            self.show_binance_unavailable(call)

        @self.bot.callback_query_handler(func=lambda call: call.data.startswith("star_package:"))
        def handle_star_package(call):
            package = call.data.split(":")[1]
            self.process_star_payment(call, package)

        @self.bot.callback_query_handler(func=lambda call: call.data == "back_to_recharge_main")
        def handle_back_to_recharge(call):
            self.show_main_recharge_menu(call)

        @self.bot.callback_query_handler(func=lambda call: call.data == "charge_balance")
        def handle_charge_balance(call):
            self.show_charge_balance_menu(call)

        @self.bot.callback_query_handler(func=lambda call: call.data == "recharge_with_admin")
        def handle_recharge_with_admin(call):
            self.show_admin_contact(call)

        @self.bot.callback_query_handler(func=lambda call: call.data == "my_balance")
        def handle_my_balance(call):
            self.show_my_balance(call)

        @self.bot.callback_query_handler(func=lambda call: call.data == "back_to_main_from_payment")
        def handle_back_to_main(call):
            self.show_main_menu(call)

        @self.bot.callback_query_handler(func=lambda call: call.data == "admins_list")
        def handle_admins_list(call):
            self.show_admins_list(call)

        @self.bot.pre_checkout_query_handler(func=lambda query: True)
        def checkout(pre_checkout_query):
            self.bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

        @self.bot.message_handler(content_types=['successful_payment'])
        def got_payment(message):
            self.handle_successful_payment(message)

        @self.bot.message_handler(commands=['start'])
        def handle_start(message):
            self.handle_start_command(message)

        @self.bot.callback_query_handler(func=lambda call: call.data == "stats")
        def handle_stats(call):
            self.show_stats(call)

        @self.bot.callback_query_handler(func=lambda call: call.data == "go_to_main_bot")
        def handle_go_to_main_bot(call):
            self.go_to_main_bot(call)

        @self.bot.callback_query_handler(func=lambda call: call.data == "admin_panel")
        def handle_admin_panel(call):
            self.show_admin_panel(call)

        @self.bot.callback_query_handler(func=lambda call: call.data == "admin_users")
        def handle_admin_users(call):
            self.show_admin_users(call)

        @self.bot.callback_query_handler(func=lambda call: call.data == "admin_transactions")
        def handle_admin_transactions(call):
            self.show_admin_transactions(call)

        @self.bot.callback_query_handler(func=lambda call: call.data == "admin_binance")
        def handle_admin_binance(call):
            self.show_admin_binance(call)

        @self.bot.message_handler(commands=['admin'])
        def handle_admin_command(message):
            self.show_admin_panel_message(message)

    def create_star_packages_keyboard(self):
        """إنشاء لوحة أزرار حزم النجوم"""
        keyboard = InlineKeyboardMarkup()

        packages = [
            {"stars": 100, "dollars": 7.39, "text": "100 ⭐ - 7.39 ﷼"},
            {"stars": 250, "dollars": 17.39, "text": "250 ⭐ - 17.39 ﷼"},
            {"stars": 500, "dollars": 33.99, "text": "500 ⭐ - 33.99 ﷼"},
            {"stars": 1000, "dollars": 67.99, "text": "1000 ⭐ - 67.99 ﷼"},
            {"stars": 2000, "dollars": 167.99, "text": "2000 ⭐ - 167.99 ﷼"},
            {"stars": 5000, "dollars": 669.00, "text": "5000 ⭐ - 669.00 ﷼"}
        ]

        for i in range(0, len(packages), 2):
            row = []
            if i < len(packages):
                row.append(InlineKeyboardButton(
                    packages[i]["text"],
                    callback_data=f"star_package:{packages[i]['stars']}"
                ))
            if i + 1 < len(packages):
                row.append(InlineKeyboardButton(
                    packages[i + 1]["text"],
                    callback_data=f"star_package:{packages[i + 1]['stars']}"
                ))
            if row:
                keyboard.add(*row)

        keyboard.add(InlineKeyboardButton("رجوع", callback_data="back_to_recharge_main"))
        keyboard.add(InlineKeyboardButton("القائمة الرئيسية", callback_data="back_to_main_from_payment"))

        return keyboard

    def create_main_recharge_keyboard(self):
        """إنشاء لوحة أزرار الشحن الرئيسية"""
        keyboard = InlineKeyboardMarkup()

        keyboard.add(InlineKeyboardButton(" شحن الرصيد", callback_data="charge_balance"))
        keyboard.add(InlineKeyboardButton("💳 رصيدي", callback_data="my_balance"))
        keyboard.add(InlineKeyboardButton("📊 الإحصائيات", callback_data="stats"))
        keyboard.add(
            InlineKeyboardButton("@QQ7iBOT", url="https://t.me/QQ7iBOT"),
            InlineKeyboardButton("@QQ7iBOT", url="https://t.me/QQ7iBOT")
        )

        return keyboard

    def create_admin_main_keyboard(self):
        """إنشاء لوحة أزرار للمشرفين مع زر لوحة التحكم"""
        keyboard = InlineKeyboardMarkup()

        keyboard.add(InlineKeyboardButton(" شحن الرصيد", callback_data="charge_balance"))
        keyboard.add(InlineKeyboardButton("💳 رصيدي", callback_data="my_balance"))
        keyboard.add(InlineKeyboardButton("📊 الإحصائيات", callback_data="stats"))
        keyboard.add(InlineKeyboardButton("👑 لوحة تحكم المشرف", callback_data="admin_panel"))
        keyboard.add(
            InlineKeyboardButton("@QQ7iBOT", url="https://t.me/QQ7iBOT"),
            InlineKeyboardButton("@QQ7iBOT", url="https://t.me/QQ7iBOT")
        )

        return keyboard

    def show_main_recharge_menu(self, call):
        """عرض قائمة الشحن الرئيسية"""
        user_id = call.from_user.id
        balance = self.get_user_balance(user_id)

        message_text = (
            f"🤖︙ **مرحباً بك في ᴋʏᴀɴ sɪᴍ_ʙᴏᴛ - بوت الشحن**\n\n"
            f"💰︙ **منصة آمنة وموثوقة لشحن الرصيد**\n\n"
            f"🆔︙ **ايديك:** `{user_id}`\n"
            f"💳︙ **رصيدك:** {balance:.2f} $\n\n"
            f"🛡︙ **جميع التحويلات آمنة وسريعة**\n"
            f"⚡︙ **رصيدك آمن معنا**\n\n"
            f"📊︙ **إبدأ الآن باستخدام الأزرار أدناه:**"
        )

        # استخدام لوحة مختلفة للمشرفين
        if self.is_admin(user_id):
            keyboard = self.create_admin_main_keyboard()
        else:
            keyboard = self.create_main_recharge_keyboard()

        try:
            self.bot.edit_message_text(
                message_text,
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
        except:
            self.bot.send_message(
                call.message.chat.id,
                message_text,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )

        self.bot.answer_callback_query(call.id)

    def show_star_packages(self, call):
        """عرض حزم النجوم المتاحة"""
        message_text = (
            "**💰 شحن الرصيد بالنجوم**\n\n"
            "**⭐ اختر  النجوم الي تريد دفعها مقابل رصيد في البوت**\n\n"
            "**📝 ملاحظة:** بعد الدفع سيتم إضافة الرصيد تلقائياً لحسابك في البوت الرئيسي."
        )

        try:
            self.bot.edit_message_text(
                message_text,
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=self.create_star_packages_keyboard(),
                parse_mode='Markdown'
            )
        except:
            self.bot.send_message(
                call.message.chat.id,
                message_text,
                reply_markup=self.create_star_packages_keyboard(),
                parse_mode='Markdown'
            )

        self.bot.answer_callback_query(call.id)

    def show_main_menu(self, call):
        """عرض القائمة الرئيسية"""
        user_id = call.from_user.id
        balance = self.get_user_balance(user_id)

        message_text = (
            f"**🎮 بوت شحن الرصيد**\n\n"
            f"🆔 ايديك: `{user_id}`\n"
            f"💰 رصيدك: {balance:.2f} $\n\n"
            f"اختر من الأزرار أدناه:"
        )

        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("شحن الرصيد", callback_data="back_to_recharge_main"))

        keyboard.add(
            InlineKeyboardButton("إحصائيات", callback_data="stats"),
            InlineKeyboardButton("البوت الرئيسي", callback_data="go_to_main_bot")
        )

        try:
            self.bot.edit_message_text(
                message_text,
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
        except:
            self.bot.send_message(
                call.message.chat.id,
                message_text,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )

        self.bot.answer_callback_query(call.id)

    def show_admins_list(self, call):
        message_text = (
            "**👨‍💻 مرحباً بك في دعم العملاء**\n\n"      "**📌- للاستفسارات وحلول مشاكل في البوت**\n\n"
            "**📑- للمساعدة وتعليمات البوت**\n"
            "**🛠- لاقتراحات في تطوير البوت**\n"
            "**⚙-فقط قم بضغط الزر و ارسل رسالتك**\n"
        )

        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("الدعم", url="https://t.me/QQ7iBOT"))
        keyboard.add(InlineKeyboardButton("شحن بالنجوم", callback_data="recharge_with_stars"))
        keyboard.add(InlineKeyboardButton("رجوع", callback_data="back_to_recharge_main"))

        try:
            self.bot.edit_message_text(
                message_text,
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
        except:
            self.bot.send_message(
                call.message.chat.id,
                message_text,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )

        self.bot.answer_callback_query(call.id)

    def show_binance_unavailable(self, call):
        """عرض رسالة أن خدمة Binance غير متوفرة"""
        message_text = (
            "**🚫 الخدمة غير متوفرة قريباً**\n\n"
            "نعتذر عن عدم توفر خدمة الشحن عبر Binance في الوقت الحالي.\n\n"
            "يرجى الاستفادة من الخدمات الأخرى المتاحة."
        )

        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("رجوع", callback_data="back_to_recharge_main"))

        try:
            self.bot.edit_message_text(
                message_text,
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
        except:
            self.bot.send_message(
                call.message.chat.id,
                message_text,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )

        self.bot.answer_callback_query(call.id)

    def show_stats(self, call):
        """عرض إحصائيات المستخدم"""
        user_id = call.from_user.id
        balance = self.get_user_balance(user_id)
        payment_history = self.get_payment_history(user_id)
        total_spent = sum(payment['dollars_amount'] for payment in payment_history)

        message_text = (
            f"**📊 إحصائياتك**\n\n"
            f"🆔 ايديك: `{user_id}`\n"
            f"💰 الرصيد الحالي: {balance:.2f} $\n"
            f"💸 إجمالي المشتريات: {total_spent:.2f} $\n"
            f"🛒 عدد عمليات الشحن: {len(payment_history)}\n\n"
        )

        if payment_history:
            message_text += "**📋 آخر العمليات:**\n"
            for i, payment in enumerate(payment_history[-3:], 1):
                message_text += f"{i}. {payment['dollars_amount']:.2f}$ - {payment['timestamp']}\n"

        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("شحن الرصيد", callback_data="back_to_recharge_main"))

        keyboard.add(
            InlineKeyboardButton("إحصائيات", callback_data="stats"),
            InlineKeyboardButton("البوت الرئيسي", callback_data="go_to_main_bot")
        )

        keyboard.add(InlineKeyboardButton("رجوع", callback_data="back_to_main_from_payment"))

        try:
            self.bot.edit_message_text(
                message_text,
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
        except:
            self.bot.send_message(
                call.message.chat.id,
                message_text,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )

        self.bot.answer_callback_query(call.id)

    def go_to_main_bot(self, call):
        """الذهاب إلى البوت الرئيسي"""
        if self.main_bot_username:
            main_bot_url = f"https://t.me/{self.main_bot_username}?start=from_payment_bot"
            message_text = (
                "**🚀 انتقل إلى البوت الرئيسي**\n\n"
                "انقر على الزر أدناه للذهاب إلى البوت الرئيسي:\n"
            )

            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton("الذهاب للبوت الرئيسي", url=main_bot_url))
            keyboard.add(InlineKeyboardButton("رجوع", callback_data="back_to_main_from_payment"))

            try:
                self.bot.edit_message_text(
                    message_text,
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    reply_markup=keyboard,
                    parse_mode='Markdown'
                )
            except:
                self.bot.send_message(
                    call.message.chat.id,
                    message_text,
                    reply_markup=keyboard,
                    parse_mode='Markdown'
                )
        else:
            self.bot.answer_callback_query(
                call.id,
                "❌ لم يتم تعيين معرف البوت الرئيسي",
                show_alert=True
            )

        self.bot.answer_callback_query(call.id)

    def process_star_payment(self, call, stars_amount):
        """معالجة دفع النجوم"""
        stars_amount = int(stars_amount)
        # كل 100 نجمة = 5 ريال سعودي
        riyal_amount = (stars_amount / 100) * 5

        title = f"شحن رصيد بقيمة {riyal_amount:.2f} ﷼"
        description = f"شراء {stars_amount} نجمة لشحن رصيد بقيمة {riyal_amount:.2f} ﷼ في البوت"

        try:
            self.bot.send_invoice(
                chat_id=call.message.chat.id,
                title=title,
                description=description,
                provider_token="",
                currency="XTR",
                prices=[LabeledPrice(label=f"{stars_amount} نجمة", amount=stars_amount)],
                start_parameter=f"star_payment_{stars_amount}",
                invoice_payload=f"star_payment_{stars_amount}_{call.message.chat.id}"
            )
        except Exception as e:
            error_msg = f"❌ حدث خطأ في إنشاء الفاتورة: {str(e)}"
            self.bot.send_message(call.message.chat.id, error_msg)

        self.bot.answer_callback_query(call.id)

    def verify_binance_payment(self, txid, amount):
        """التحقق من معاملة Binance"""
        endpoint = 'https://api3.binance.com/sapi/v1/pay/transactions'
        params = {
            'timestamp': int(time.time() * 1000),
            'status': '1',
            'startTime': (int(time.time()) - 7200) * 1000,
            'endTime': int(time.time()) * 1000,
            'limit': 100
        }

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
            data = response.json()

            if not data or 'data' not in data:
                return False

            for transaction in data['data']:
                t_order_id = str(transaction.get('orderId', ''))
                t_trans_id = str(transaction.get('transactionId', ''))

                if t_order_id == str(txid) or t_trans_id == str(txid):
                    if (transaction.get('currency') == 'USDT' and
                            abs(float(transaction.get('amount', 0)) - float(amount)) < 0.1):
                        return True
            return False
        except Exception as e:
            print(f"Binance API Error: {e}")
            return False

    def is_txid_used(self, txid):
        """التحقق مما إذا كان رقم العملية مستخدم مسبقاً"""
        for user_payments in self.payment_data.values():
            for payment in user_payments:
                if payment.get('txid') == str(txid):
                    return True
        return False

    def start_binance_flow(self, call):
        """بدء عملية الشحن عبر Binance"""
        msg = self.bot.send_message(
            call.message.chat.id,
            "**💰 الشحن عبر Binance**\n\n"
            "💵 **أرسل المبلغ الذي ترغب في شحنه (USDT):**\n"
            "مثال: 5 أو 10.5\n\n"
            "❌ للإلغاء أرسل /cancel",
            parse_mode='Markdown'
        )
        self.bot.register_next_step_handler(msg, self.process_binance_amount)
        self.bot.answer_callback_query(call.id)

    def process_binance_amount(self, message):
        """معالجة المبلغ المدخل"""
        if message.text == '/cancel':
            self.bot.send_message(message.chat.id, "❌ تم الإلغاء.")
            return

        try:
            amount = float(message.text)
            if amount < 1:
                msg = self.bot.send_message(message.chat.id, "❌ الحد الأدنى للشحن هو 1$. حاول مرة أخرى:")
                self.bot.register_next_step_handler(msg, self.process_binance_amount)
                return

            text = (
                f"💰 **تعليمات الدفع**\n\n"
                f"1️⃣ قم بتحويل **{amount} USDT** بالضبط إلى:\n"
                f"🆔 Pay ID / Wallet: `{BINANCE_WALLET}`\n\n"
                f"2️⃣ بعد التحويل، انسخ **رقم العملية (Order ID)** وأرسله هنا.\n\n"
                f"👇 **أرسل رقم العملية الآن:**"
            )
            msg = self.bot.send_message(message.chat.id, text, parse_mode='Markdown')
            self.bot.register_next_step_handler(msg, self.process_binance_txid, amount)

        except ValueError:
            msg = self.bot.send_message(message.chat.id, "❌ الرجاء إدخال رقم صحيح. حاول مرة أخرى:")
            self.bot.register_next_step_handler(msg, self.process_binance_amount)

    def process_binance_txid(self, message, amount):
        """معالجة رقم العملية والتحقق"""
        if message.text == '/cancel':
            self.bot.send_message(message.chat.id, "❌ تم الإلغاء.")
            return

        txid = message.text.strip()

        if self.is_txid_used(txid):
            self.bot.send_message(message.chat.id, "❌ رقم العملية هذا مستخدم مسبقاً!")
            return

        wait_msg = self.bot.send_message(message.chat.id, "🔄 جاري التحقق من العملية...")

        if self.verify_binance_payment(txid, amount):
            if self.add_balance_to_user(message.chat.id, amount):
                current_time = self.get_formatted_time()
                payment_record = {
                    'user_id': message.chat.id,
                    'username': message.from_user.username,
                    'first_name': message.from_user.first_name,
                    'stars_amount': 0,
                    'dollars_amount': amount,
                    'txid': txid,
                    'method': 'binance',
                    'timestamp': current_time
                }

                if str(message.chat.id) not in self.payment_data:
                    self.payment_data[str(message.chat.id)] = []
                self.payment_data[str(message.chat.id)].append(payment_record)
                self.save_payment_data()

                self.bot.delete_message(message.chat.id, wait_msg.message_id)
                self.bot.send_message(
                    message.chat.id,
                    f"✅ **تم الشحن بنجاح!**\n\n💰 المبلغ المضاف: {amount}$\n🆔 رقم العملية: `{txid}`",
                    parse_mode='Markdown'
                )

                self.bot.send_message(self.admin_id,
                                      f"💰 **شحن Binance جديد**\n👤 المستخدم: {message.chat.id}\n💵 المبلغ: {amount}$\n🆔 TXID: {txid}")
        else:
            self.bot.delete_message(message.chat.id, wait_msg.message_id)
            self.bot.send_message(message.chat.id,
                                  "❌ فشل التحقق. تأكد من رقم العملية والمبلغ (يجب أن يكون مطابقاً تماماً) وأن التحويل تم خلال آخر ساعتين.")

    def handle_successful_payment(self, message):
        """معالجة الدفع الناجح"""
        try:
            payment_info = message.successful_payment
            invoice_payload = payment_info.invoice_payload

            parts = invoice_payload.split("_")
            if len(parts) >= 4 and parts[0] == "star" and parts[1] == "payment":
                stars_amount = int(parts[2])
                user_id = int(parts[3])

                # كل 100 نجمة = 5 ريال سعودي
                riyal_amount = (stars_amount / 100) * 5

                success = self.add_balance_to_user(user_id, riyal_amount)

                if success:
                    current_balance = self.get_user_balance(user_id)
                    current_time = self.get_formatted_time()

                    user_notification = (
                        f"✅ تم شحن رصيدك بنجاح\n\n"
                    )

                    self.bot.send_message(
                        user_id,
                        user_notification,
                        parse_mode='Markdown'
                    )

                    admin_notification = (
                        f"💫 عملية شحن ناجحة عزيزي المالك\n\n"
                        f"👤 المستخدم: {message.from_user.first_name}\n"
                        f"🆔 الايديك: {user_id}\n"
                        f"📧 اليوزر: @{message.from_user.username or 'لا يوجد'}\n"
                        f"💰 المبلغ: {riyal_amount:.2f} ﷼\n"
                        f"💰 رصيده: {current_balance:.2f} ﷼\n"
                        f"⭐ النجوم: {stars_amount}\n"
                        f"📅 الوقت: {current_time}"
                    )

                    self.bot.send_message(
                        self.admin_id,
                        admin_notification,
                        parse_mode='Markdown'
                    )

                    if self.main_bot_username:
                        try:
                            main_bot_url = f"https://t.me/{self.main_bot_username}?start=payment_success"
                            success_logo = (
                                f"✅ تم شحن حسابك بنجاح\n\n"
                                f"⭐️ • النجوم: {stars_amount}\n"
                                f"💰 • المبلغ المضاف: {riyal_amount:.2f} ﷼\n"
                                f"💰 • رصيدك الحالي: {current_balance:.2f} ﷼\n"
                                f"📅 • الوقت والتاريخ: {current_time}\n\n"
                                f"اضغط الزر للدخول الى البوت 👇"
                            )

                            keyboard = InlineKeyboardMarkup()
                            keyboard.add(InlineKeyboardButton("الدخول الى البوت", url=main_bot_url))

                            self.bot.send_message(
                                user_id,
                                success_logo,
                                reply_markup=keyboard,
                                parse_mode='Markdown'
                            )
                        except Exception as e:
                            print(f"⚠️ لم يتم إرسال الشعار للبوت الرئيسي: {e}")

                    payment_record = {
                        'user_id': user_id,
                        'username': message.from_user.username,
                        'first_name': message.from_user.first_name,
                        'stars_amount': stars_amount,
                        'riyal_amount': riyal_amount,
                        'new_balance': current_balance,
                        'method': 'stars',
                        'timestamp': current_time
                    }

                    if str(user_id) not in self.payment_data:
                        self.payment_data[str(user_id)] = []

                    self.payment_data[str(user_id)].append(payment_record)
                    self.save_payment_data()

                else:
                    raise Exception("فشل في تحديث رصيد المستخدم")

            else:
                raise ValueError("تنسيق payload غير صحيح")

        except Exception as e:
            error_msg = f"❌ حدث خطأ في معالجة الدفع: {str(e)}"
            self.bot.send_message(message.chat.id, error_msg)

            self.bot.send_message(
                self.admin_id,
                f"🚨 خطأ في معالجة الدفع:\n\nالمستخدم: {message.chat.id}\nالخطأ: {str(e)}"
            )

    def handle_start_command(self, message):
        """معالجة أمر /start"""
        user_id = message.chat.id
        balance = self.get_user_balance(user_id)

        welcome_text = (
            f"🤖︙ **مرحباً بك في ᴋʏᴀɴ sɪᴍ_ʙᴏᴛ - بوت الشحن**\n\n"
            f"💰︙ **منصة آمنة وموثوقة لشحن الرصيد**\n\n"
            f"🆔︙ **ايديك:** `{user_id}`\n"
            f"💳︙ **رصيدك:** {balance:.2f} $\n\n"
            f"🛡︙ **جميع التحويلات آمنة وسريعة**\n"
            f"⚡︙ **رصيدك آمن معنا**\n\n"
            f"📊︙ **إبدأ الآن باستخدام الأزرار أدناه:**"
        )

        self.bot.send_message(
            user_id,
            welcome_text,
            parse_mode='Markdown',
            reply_markup=self.create_main_recharge_keyboard()
        )

    def add_balance_to_user(self, user_id, amount):
        """إضافة رصيد للمستخدم"""
        try:
            user_key = f"user_{user_id}"
            if self.db.exists(user_key):
                user_data = self.db.get(user_key)
                user_data["coins"] += amount
                self.db.set(user_key, user_data)
            else:
                user_data = {"coins": amount, "id": user_id}
                self.db.set(user_key, user_data)
            return True
        except Exception as e:
            print(f"خطأ في إضافة الرصيد: {e}")
            return False

    def get_user_balance(self, user_id):
        """الحصول على رصيد المستخدم"""
        try:
            user_key = f"user_{user_id}"
            if self.db.exists(user_key):
                user_data = self.db.get(user_key)
                return user_data.get("coins", 0)
            return 0
        except:
            return 0

    def get_formatted_time(self):
        """الحصول على الوقت الحالي بصيغة منظمة"""
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def get_payment_history(self, user_id):
        """الحصول على سجل الدفع للمستخدم"""
        user_id_str = str(user_id)
        if user_id_str in self.payment_data:
            return self.payment_data[user_id_str]
        return []

    def get_total_earnings(self):
        """الحصول على إجمالي الأرباح"""
        total = 0
        for user_payments in self.payment_data.values():
            for payment in user_payments:
                total += payment['dollars_amount']
        return total

    def is_admin(self, user_id):
        """التحقق من أن المستخدم مشرف"""
        return user_id in self.admins_list

    def show_admin_panel_message(self, message):
        """عرض لوحة تحكم المشرفين من رسالة"""
        if not self.is_admin(message.from_user.id):
            self.bot.send_message(message.chat.id, "❌ عذراً، هذا الأمر للمشرفين فقط!")
            return

        # حساب الإحصائيات
        total_users = 0
        total_balance = 0.0
        total_deposits = 0.0

        # حساب عدد المستخدمين
        try:
            all_keys = self.db.keys()
            for key in all_keys:
                if key.startswith("user_"):
                    total_users += 1
                    user_data = self.db.get(key)
                    total_balance += user_data.get("coins", 0)
        except:
            pass

        # حساب إجمالي الإيداعات
        for user_payments in self.payment_data.values():
            for payment in user_payments:
                total_deposits += payment.get('riyal_amount', 0)

        message_text = (
            f"👑 **لوحة تحكم المشرف**\n\n"
            f"📊 **إحصائيات البوت:**\n"
            f"• 👥 إجمالي المستخدمين: {total_users}\n"
            f"• 💰 إجمالي الأرصدة: {total_balance:.2f} ﷼\n"
            f"• 💳 إجمالي الإيداعات: {total_deposits:.2f} ﷼\n\n"
            f"⚙️ **خيارات الإدارة:**"
        )

        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("👥 قائمة المستخدمين", callback_data="admin_users"))
        keyboard.add(InlineKeyboardButton("💳 جميع المعاملات", callback_data="admin_transactions"))
        keyboard.add(InlineKeyboardButton("⚙️ إعدادات البوت", callback_data="admin_binance"))
        keyboard.add(InlineKeyboardButton("🔙 رجوع", callback_data="back_to_recharge_main"))

        self.bot.send_message(
            message.chat.id,
            message_text,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )

    def show_admin_panel(self, call):
        """عرض لوحة تحكم المشرفين من callback"""
        if not self.is_admin(call.from_user.id):
            self.bot.answer_callback_query(call.id, "❌ عذراً، هذا للمشرفين فقط!", show_alert=True)
            return

        # حساب الإحصائيات
        total_users = 0
        total_balance = 0.0
        total_deposits = 0.0

        # حساب عدد المستخدمين
        try:
            all_keys = self.db.keys()
            for key in all_keys:
                if key.startswith("user_"):
                    total_users += 1
                    user_data = self.db.get(key)
                    total_balance += user_data.get("coins", 0)
        except:
            pass

        # حساب إجمالي الإيداعات
        for user_payments in self.payment_data.values():
            for payment in user_payments:
                total_deposits += payment.get('riyal_amount', 0)

        message_text = (
            f"👑 **لوحة تحكم المشرف**\n\n"
            f"📊 **إحصائيات البوت:**\n"
            f"• 👥 إجمالي المستخدمين: {total_users}\n"
            f"• 💰 إجمالي الأرصدة: {total_balance:.2f} ﷼\n"
            f"• 💳 إجمالي الإيداعات: {total_deposits:.2f} ﷼\n\n"
            f"⚙️ **خيارات الإدارة:**"
        )

        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("👥 قائمة المستخدمين", callback_data="admin_users"))
        keyboard.add(InlineKeyboardButton("💳 جميع المعاملات", callback_data="admin_transactions"))
        keyboard.add(InlineKeyboardButton("⚙️ إعدادات البوت", callback_data="admin_binance"))
        keyboard.add(InlineKeyboardButton("🔙 رجوع", callback_data="back_to_recharge_main"))

        try:
            self.bot.edit_message_text(
                message_text,
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
        except:
            self.bot.send_message(
                call.message.chat.id,
                message_text,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )

        self.bot.answer_callback_query(call.id)

    def show_admin_users(self, call):
        """عرض قائمة المستخدمين للمشرفين"""
        if not self.is_admin(call.from_user.id):
            self.bot.answer_callback_query(call.id, "❌ عذراً، هذا للمشرفين فقط!", show_alert=True)
            return

        users_list = []
        try:
            all_keys = self.db.keys()
            for key in all_keys:
                if key.startswith("user_"):
                    user_data = self.db.get(key)
                    user_id = user_data.get("id", 0)
                    balance = user_data.get("coins", 0)
                    users_list.append((user_id, balance))
        except Exception as e:
            print(f"خطأ في جلب المستخدمين: {e}")

        if not users_list:
            message_text = "📭 **لا يوجد مستخدمين مسجلين بعد**"
        else:
            # ترتيب حسب الرصيد (الأعلى أولاً)
            users_list.sort(key=lambda x: x[1], reverse=True)

            message_text = f"👥 **قائمة المستخدمين** ({len(users_list)} مستخدم)\n\n"

            # عرض أول 10 مستخدمين
            for i, (user_id, balance) in enumerate(users_list[:10], 1):
                message_text += f"{i}. ID: `{user_id}` - 💰 {balance:.2f} ﷼\n"

            if len(users_list) > 10:
                message_text += f"\n... و {len(users_list) - 10} مستخدم آخر"

        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("🔙 رجوع للوحة التحكم", callback_data="admin_panel"))

        try:
            self.bot.edit_message_text(
                message_text,
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
        except:
            self.bot.send_message(
                call.message.chat.id,
                message_text,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )

        self.bot.answer_callback_query(call.id)

    def show_admin_transactions(self, call):
        """عرض جميع المعاملات للمشرفين"""
        if not self.is_admin(call.from_user.id):
            self.bot.answer_callback_query(call.id, "❌ عذراً، هذا للمشرفين فقط!", show_alert=True)
            return

        all_transactions = []
        for user_id, payments in self.payment_data.items():
            for payment in payments:
                all_transactions.append({
                    'user_id': user_id,
                    'username': payment.get('username', 'N/A'),
                    'amount': payment.get('riyal_amount', 0),
                    'stars': payment.get('stars_amount', 0),
                    'method': payment.get('method', 'N/A'),
                    'timestamp': payment.get('timestamp', 'N/A')
                })

        if not all_transactions:
            message_text = "📭 **لا توجد معاملات بعد**"
        else:
            # ترتيب حسب التاريخ (الأحدث أولاً)
            all_transactions.sort(key=lambda x: x['timestamp'], reverse=True)

            total_amount = sum(t['amount'] for t in all_transactions)

            message_text = (
                f"💳 **جميع المعاملات** ({len(all_transactions)} معاملة)\n"
                f"💰 **الإجمالي:** {total_amount:.2f} ﷼\n\n"
            )

            # عرض آخر 5 معاملات
            for i, trans in enumerate(all_transactions[:5], 1):
                message_text += (
                    f"{i}. @{trans['username']}\n"
                    f"   💰 {trans['amount']:.2f} ﷼ | ⭐ {trans['stars']}\n"
                    f"   📅 {trans['timestamp']}\n\n"
                )

            if len(all_transactions) > 5:
                message_text += f"... و {len(all_transactions) - 5} معاملة أخرى"

        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("🔙 رجوع للوحة التحكم", callback_data="admin_panel"))

        try:
            self.bot.edit_message_text(
                message_text,
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
        except:
            self.bot.send_message(
                call.message.chat.id,
                message_text,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )

        self.bot.answer_callback_query(call.id)

    def show_admin_binance(self, call):
        """عرض إعدادات Binance للمشرفين"""
        if not self.is_admin(call.from_user.id):
            self.bot.answer_callback_query(call.id, "❌ عذراً، هذا للمشرفين فقط!", show_alert=True)
            return

        binance_status = "✅ متصل" if BINANCE_API_KEY and BINANCE_SECRET_KEY else "❌ غير متصل"

        message_text = (
            f"⚙️ **إعدادات البوت**\n\n"
            f"🔗 **حالة Binance:** {binance_status}\n"
            f"💰 **محفظة Binance:** `{BINANCE_WALLET or 'غير محددة'}`\n"
            f"⭐ **سعر النجمة:** 100 نجمة = 5 ﷼\n\n"
            f"📊 **البوت الرئيسي:** @{self.main_bot_username or 'غير محدد'}\n"
            f"👥 **عدد المشرفين:** {len(self.admins_list)}"
        )

        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("🔙 رجوع للوحة التحكم", callback_data="admin_panel"))

        try:
            self.bot.edit_message_text(
                message_text,
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
        except:
            self.bot.send_message(
                call.message.chat.id,
                message_text,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )

        self.bot.answer_callback_query(call.id)

    def start_polling(self):
        """بدء استطلاع البوت"""
        try:
            print("🔄 جاري تشغيل نظام الدفع بالنجوم...")
            self.bot.infinity_polling(timeout=60, long_polling_timeout=60)
        except Exception as e:
            print(f"❌ خطأ في تشغيل نظام الدفع: {e}")

    def show_charge_balance_menu(self, call):
        """عرض خيارات الشحن الثلاث"""
        message_text = (
            "**💰 طرق الشحن المتاحة:**\n\n"
            "**1️⃣ شحن بالنجوم** ⭐\n"
            "   - دفع سريع وآمن عبر نجوم تيليجرام\n"
            "   - حزم متعددة من 25 إلى 1000 نجمة\n\n"
            "**2️⃣ شحن عبر وكيل الشحن** 💳\n"
            "   - تحويل بنكي مباشر\n"
            "   - عملات رقمية (USDT, LTC, TON)\n\n"
            "**3️⃣ Binance** 🔗\n"
            "   - غير متوفر حالياً\n\n"
            "اختر طريقة الشحن من الأزرار أدناه:"
        )

        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("⭐ شحن بالنجوم", callback_data="recharge_with_stars"))
        keyboard.add(InlineKeyboardButton("💳 شحن عبر وكيل الشحن", callback_data="recharge_with_admin"))
        keyboard.add(InlineKeyboardButton("🔗 Binance (غير متوفر)", callback_data="recharge_with_binance"))
        keyboard.add(InlineKeyboardButton("🔙 رجوع", callback_data="back_to_recharge_main"))

        try:
            self.bot.edit_message_text(
                message_text,
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
        except:
            self.bot.send_message(
                call.message.chat.id,
                message_text,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )

        self.bot.answer_callback_query(call.id)

    def show_my_balance(self, call):
        """عرض رصيد المستخدم"""
        user_id = call.from_user.id
        balance = self.get_user_balance(user_id)

        message_text = (
            f"💳︙**رصيدك الحالي:**\n\n"
            f"💰︙ `{balance:.2f} $`\n\n"
            f"📥︙**لشحن رصيدك إضغط على زر شحن الرصيد**"
        )

        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(" شحن الرصيد", callback_data="charge_balance"))
        keyboard.add(InlineKeyboardButton("🔙 رجوع", callback_data="back_to_recharge_main"))

        try:
            self.bot.edit_message_text(
                message_text,
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
        except:
            self.bot.send_message(
                call.message.chat.id,
                message_text,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )

        self.bot.answer_callback_query(call.id)

    def show_admin_contact(self, call):
        """عرض خيارات الشحن عبر المالك"""
        message_text = (
            "**💳 طرق الشحن عبر وكيل الشحن:**\n\n"
            "اختر الطريقة المناسبة للتحويل:\n\n"
            "1️⃣ **التحويل البنكي** - تحويل عبر البنك\n"
            "2️⃣ **العملات الرقمية** - USDT و LTC و TON\n\n"
            "يمكنك التواصل مع الدعم الفني لتسجيل التحويل والتأكيد."
        )

        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("  @QQ7iBOT", url="https://t.me/QQ7iBOT"))
        keyboard.add(InlineKeyboardButton("🔙 رجوع", callback_data="back_to_recharge_main"))

        try:
            self.bot.edit_message_text(
                message_text,
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
        except:
            self.bot.send_message(
                call.message.chat.id,
                message_text,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )

        self.bot.answer_callback_query(call.id)


def create_payment_system(bot_token, admin_id, db, main_bot_username=None):
    """إنشاء وإرجاع نظام الدفع"""
    return TelegramStarsPaymentSystem(bot_token, admin_id, db, main_bot_username)


def get_stars_recharge_button():
    """إرجاع زر شحن النجوم للبوت الرئيسي"""
    from telebot.types import InlineKeyboardButton
    return InlineKeyboardButton("شحن بالنجوم", callback_data="recharge_with_stars")


def get_payment_bot_link(payment_bot_username):
    """إرجاع رابط بوت الدفع"""
    return f"https://t.me/{payment_bot_username}"


if __name__ == "__main__":
    from kvsqlite.sync import Client as uu

    BOT_TOKEN = os.getenv("PAYMENT_BOT_TOKEN_2")
    ADMIN_ID = int(os.getenv("OWNER_ID", "0"))
    DB_PATH = "database/main.ss"
    MAIN_BOT_USERNAME = "RkeyStoreBOT"

    db = uu(DB_PATH, 'bot')

    payment_system = create_payment_system(BOT_TOKEN, ADMIN_ID, db, MAIN_BOT_USERNAME)
    print("🚀 نظام الدفع بالنجوم جاهز للعمل!")
    print(f"📱 البوت الرئيسي: @{MAIN_BOT_USERNAME}")
    payment_system.start_polling()