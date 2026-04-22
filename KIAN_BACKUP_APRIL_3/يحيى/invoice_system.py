# -*- coding: utf-8 -*-
"""
نظام الفواتير المتقدم
يقوم بإنشاء وإدارة الفواتير لكل عملية شراء أو شحن
"""

import datetime

class InvoiceSystem:
    def __init__(self, db):
        self.db = db
        self.initialize_invoices()

    def initialize_invoices(self):
        """تهيئة نظام الفواتير"""
        if not self.db.exists("invoices"):
            self.db.set("invoices", {})

    def mask_phone_number(self, phone_number):
        """
        تشفير رقم الهاتف بإخفاء 4 أرقام من المنتصف

        مثال: +201234567890 -> +2012****7890
        """
        phone_str = str(phone_number)
        # إزالة علامة + إن وجدت
        if phone_str.startswith('+'):
            phone_str = phone_str[1:]

        if len(phone_str) <= 6:
            # إذا كان الرقم قصير جداً، نخفي جزء منه فقط
            return phone_str[:2] + '****' + phone_str[-2:]

        # نخفي 4 أرقام من المنتصف
        visible_start = len(phone_str) // 2 - 2  # نبدأ قبل المنتصف
        visible_end = visible_start + 4  # نخفي 4 أرقام

        masked = phone_str[:visible_start] + '****' + phone_str[visible_end:]
        return '+' + masked

    def generate_invoice_number(self):
        """توليد رقم فاتورة فريد"""
        invoices = self.db.get("invoices")
        invoice_num = len(invoices) + 1
        return f"INV-{datetime.datetime.now().strftime('%Y%m%d')}-{invoice_num:05d}"

    def create_recharge_invoice(self, user_id, user_info, amount, method, transaction_id=None):
        """
        إنشاء فاتورة شحن رصيد

        Args:
            user_id: معرف المستخدم
            user_info: بيانات المستخدم (الاسم، اليوزرنيم، إلخ)
            amount: مبلغ الشحن
            method: طريقة الشحن (نجوم، مالك، binance)
            transaction_id: معرف العملية (اختياري)
        """
        invoice_number = self.generate_invoice_number()
        timestamp = datetime.datetime.now()

        invoice = {
            "invoice_number": invoice_number,
            "type": "recharge",
            "user_id": user_id,
            "user_name": user_info.get("first_name", "Unknown"),
            "user_username": user_info.get("username", "Unknown"),
            "amount": amount,
            "method": method,
            "transaction_id": transaction_id,
            "status": "completed",
            "timestamp": timestamp.isoformat(),
            "date": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "currency": "SAR"  # الريال السعودي
        }

        # حفظ الفاتورة في قاعدة البيانات
        invoices = self.db.get("invoices")
        invoices[invoice_number] = invoice
        self.db.set("invoices", invoices)

        return invoice

    def create_purchase_invoice(self, user_id, user_info, phone_number, country, price, account_details=None):
        """
        إنشاء فاتورة شراء رقم

        Args:
            user_id: معرف المستخدم
            user_info: بيانات المستخدم
            phone_number: الرقم المشتري
            country: الدولة
            price: السعر
            account_details: تفاصيل الحساب (اختياري)
        """
        invoice_number = self.generate_invoice_number()
        timestamp = datetime.datetime.now()

        invoice = {
            "invoice_number": invoice_number,
            "type": "purchase",
            "user_id": user_id,
            "user_name": user_info.get("first_name", "Unknown"),
            "user_username": user_info.get("username", "Unknown"),
            "phone_number": phone_number,
            "country": country,
            "price": price,
            "status": "completed",
            "timestamp": timestamp.isoformat(),
            "date": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "currency": "SAR",
            "account_details": account_details or {}
        }

        # حفظ الفاتورة في قاعدة البيانات
        invoices = self.db.get("invoices")
        invoices[invoice_number] = invoice
        self.db.set("invoices", invoices)

        return invoice

    def get_formatted_recharge_invoice(self, invoice):
        """تنسيق فاتورة الشحن للعرض"""
        message = (
            f"📄 **فاتورة شحن رصيد**\n"
            f"{'='*40}\n\n"
            f"🔢 رقم الفاتورة: {invoice['invoice_number']}\n"
            f"📅 التاريخ: {invoice['date']}\n"
            f"⏰ الوقت: {invoice['date'].split(' ')[1]}\n\n"
            f"**معلومات العميل:**\n"
            f"🆔 الايدي: {invoice['user_id']}\n"
            f"👤 الاسم: {invoice['user_name']}\n"
            f"📱 اليوزرنيم: {invoice['user_username']}\n\n"
            f"**تفاصيل الشحن:**\n"
            f"💰 المبلغ: {invoice['amount']:.2f} ﷼\n"
            f"🔧 الطريقة: {invoice['method']}\n"
            f"✅ الحالة: تم الشحن بنجاح\n"
            f"💱 العملة: {invoice['currency']}\n\n"
        )

        if invoice.get('transaction_id'):
            message += f"🔗 معرف العملية: {invoice['transaction_id']}\n\n"

        message += (
            f"{'='*40}\n"
            f"شكراً لاستخدامك خدماتنا!\n"
            f"للدعم: @FF_1i | @mYJYQD"
        )
        return message

    def get_formatted_purchase_invoice(self, invoice):
        """تنسيق فاتورة الشراء للعرض"""
        message = (
            f"📄 **فاتورة شراء رقم**\n"
            f"{'='*40}\n\n"
            f"🔢 رقم الفاتورة: {invoice['invoice_number']}\n"
            f"📅 التاريخ: {invoice['date']}\n"
            f"⏰ الوقت: {invoice['date'].split(' ')[1]}\n\n"
            f"**معلومات العميل:**\n"
            f"🆔 الايدي: {invoice['user_id']}\n"
            f"👤 الاسم: {invoice['user_name']}\n"
            f"📱 اليوزرنيم: {invoice['user_username']}\n\n"
            f"**تفاصيل الشراء:**\n"
            f"📱 الرقم: {invoice['phone_number']}\n"
            f"🌍 الدولة: {invoice['country']}\n"
            f"💰 السعر: {invoice['price']:.2f} ﷼\n"
            f"✅ الحالة: تم الشراء بنجاح\n"
            f"💱 العملة: {invoice['currency']}\n\n"
        )

        message += (
            f"{'='*40}\n"
            f"شكراً لاستخدامك خدماتنا!\n"
            f"للدعم: @FF_1i | @mYJYQD"
        )
        return message

    def get_admin_recharge_notification(self, invoice):
        """إشعار المشرف بالشحن"""
        message = (
            f"💫 **عملية شحن جديدة**\n\n"
            f"🔢 رقم الفاتورة: `{invoice['invoice_number']}`\n"
            f"🆔 ايدي العميل: `{invoice['user_id']}`\n"
            f"👤 اسم العميل: {invoice['user_name']}\n"
            f"📱 يوزرنيم: @{invoice['user_username']}\n\n"
            f"💰 المبلغ: {invoice['amount']:.2f} ﷼\n"
            f"🔧 الطريقة: {invoice['method']}\n"
            f"📅 الوقت: {invoice['date']}\n"
            f"✅ الحالة: تم الشحن بنجاح"
        )
        return message

    def get_admin_purchase_notification(self, invoice):
        """إشعار المشرف بالشراء"""
        message = (
            f"🛒 **عملية شراء جديدة**\n\n"
            f"🔢 رقم الفاتورة: `{invoice['invoice_number']}`\n"
            f"🆔 ايدي العميل: `{invoice['user_id']}`\n"
            f"👤 اسم العميل: {invoice['user_name']}\n"
            f"📱 يوزرنيم: @{invoice['user_username']}\n\n"
            f"📱 الرقم: {invoice['phone_number']}\n"
            f"🌍 الدولة: {invoice['country']}\n"
            f"💰 السعر: {invoice['price']:.2f} ﷼\n"
            f"📅 الوقت: {invoice['date']}\n"
            f"✅ الحالة: تم الشراء بنجاح"
        )
        return message

    def get_activation_channel_notification(self, invoice, bot_username):
        """
        إشعار قناة التفعيلات برقم مشفر وبدون يوزر

        Args:
            invoice: بيانات الفاتورة
            bot_username: يوزرنيم البوت للربط
        """
        masked_phone = self.mask_phone_number(invoice['phone_number'])

        message = (
            f"✅ **تم تفعيل رقم جديد بنجاح**\n\n"
            f"🌍 الدولة: {invoice['country']}\n"
            f"📱 الرقم: `{masked_phone}`\n"
            f"💰 السعر: {invoice['price']:.2f} ﷼\n"
            f"📅 التاريخ: {invoice['date']}\n\n"
            f"━━━━━━━━━━━━━━━\n"
            f"🔥 **احصل على رقمك الآن!**"
        )
        return message

    def get_all_invoices(self, user_id=None):
        """الحصول على جميع الفواتير (للمشرف أو لمستخدم معين)"""
        invoices = self.db.get("invoices")

        if user_id:
            return {k: v for k, v in invoices.items() if v.get("user_id") == user_id}

        return invoices

    def get_daily_summary(self):
        """الحصول على ملخص يومي للعمليات"""
        invoices = self.db.get("invoices")
        today = datetime.datetime.now().strftime("%Y-%m-%d")

        today_invoices = {k: v for k, v in invoices.items()
                         if v.get("date", "").startswith(today)}

        total_recharges = 0
        total_purchases = 0
        recharge_count = 0
        purchase_count = 0

        for invoice in today_invoices.values():
            if invoice.get("type") == "recharge":
                total_recharges += invoice.get("amount", 0)
                recharge_count += 1
            elif invoice.get("type") == "purchase":
                total_purchases += invoice.get("price", 0)
                purchase_count += 1

        summary = (
            f"📊 **ملخص اليوم**\n"
            f"📅 التاريخ: {today}\n\n"
            f"💫 **الشحن:**\n"
            f"  • العدد: {recharge_count}\n"
            f"  • الإجمالي: {total_recharges:.2f} ﷼\n\n"
            f"🛒 **الشراء:**\n"
            f"  • العدد: {purchase_count}\n"
            f"  • الإجمالي: {total_purchases:.2f} ﷼\n\n"
            f"💰 **الإجمالي الكلي:**\n"
            f"  {total_recharges + total_purchases:.2f} ﷼"
        )

        return summary

