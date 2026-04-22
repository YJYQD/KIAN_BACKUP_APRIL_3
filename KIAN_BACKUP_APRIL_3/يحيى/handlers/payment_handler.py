from telethon import Button


async def handle_payment(event, data, user_id, **ctx):
    db = ctx["db"]
    lang_manager = ctx["lang_manager"]
    get_formatted_currency = ctx["get_formatted_currency"]  # جلب دالة العملات

    # 1. عرض الرصيد
    if data == "show_balance":
        user_data = db.get(f"user_{user_id}") or {}
        coins = user_data.get("coins", 0)

        # استخدام دالة التنسيق لعرض الرصيد بالعملة المختارة (سعودي، يمني، دولار)
        formatted_balance = get_formatted_currency(user_id, coins)

        # جلب الرسالة المترجمة من ملف اللغة
        # يمكنك إضافة مفتاح جديد في ملف اللغة باسم BALANCE_INFO
        msg = f"💰 **معلومات الرصيد:**\n\nرصيدك الحالي هو: **{formatted_balance}**"

        buttons = [
            [Button.inline(lang_manager.get_message(user_id, 'RECHARGE_BUTTON'), data="recharge_info")],
            [Button.inline(lang_manager.get_message(user_id, 'BACK_BUTTON'), data="main")]  # زر الرجوع
        ]

        await event.edit(msg, buttons=buttons)
        return True

    # 2. عرض معلومات الشحن (Recharge)
    if data == "recharge_info":
        # جلب رسالة الشحن المترجمة من ملف اللغة
        msg = lang_manager.get_message(user_id, 'RECHARGE_MESSAGE')

        buttons = [
            [Button.url(lang_manager.get_message(user_id, 'SUPPORT_BUTTON'), "https://t.me/mYJYQD")],
            # رابط الدعم للشحن
            [Button.inline(lang_manager.get_message(user_id, 'BACK_BUTTON'), data="show_balance")]
        ]

        await event.edit(msg, buttons=buttons)
        return True

    return False