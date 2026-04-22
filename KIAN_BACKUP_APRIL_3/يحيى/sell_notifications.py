# sell_notifications.py
from telethon import Button
from datetime import datetime

class SellNotifications:
    def __init__(self, db, client):
        self.db = db
        self.client = client

    def set_sell_notification_channel(self, channel):
        """تعيين القناة للإشعارات"""
        self.db.set("sell_notification_channel", channel)

    def get_sell_notification_channel(self):
        """الحصول على القناة المخصصة للإشعارات"""
        return self.db.get("sell_notification_channel") if self.db.exists("sell_notification_channel") else None

    async def send_sell_notification(self, country_info, calling_code, seller_id, sell_price):
        """إرسال إشعار بيع إلى القناة المخصصة"""
        channel = self.get_sell_notification_channel()
        if not channel:
            return

        # استخراج اسم الدولة والعلم من country_info
        country_name = country_info.get('name', 'غير معروف')
        
        # تنسيق الرسالة حسب المطلوب
        message = (
            "**📮 تم بيع رقم جديد الى البوت بنجاح ✅**\n\n"
            f"**🌍 الدولة:** {country_name}\n"
            f"**📞 رمز الدولة:** +{calling_code}\n"
            f"**👤 البائع:** `{str(seller_id)[-7:]}`\n"
            f"**💰 سعر البيع:** {sell_price} $\n"
            f"**📅 التاريخ والوقت:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )

        # زر الدخول إلى البوت
        buttons = [
            [Button.url("شراء الرقم", "https://t.me/SIBANII_BOT")]
        ]

        try:
            await self.client.send_message(channel, message, buttons=buttons)
        except Exception as e:
            print(f"فشل في إرسال إشعار البيع: {e}")