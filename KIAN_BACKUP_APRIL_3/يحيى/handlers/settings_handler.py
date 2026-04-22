from telethon import Button

async def handle_settings(event, user_id, data, **ctx):
    lang = ctx["lang_manager"]
    db = ctx["db"]
    cb = ctx["cb_answer"]
    # جلب دالة عرض المنيو من السياق لتجنب الاستيراد الخارجي
    render_main = ctx.get("render_main_menu")

    # 1. القائمة الرئيسية للإعدادات
    if data == "settings_menu":
        await event.edit(
            lang.get_message(user_id, 'SETTINGS_MENU_MESSAGE'),
            buttons=lang.get_settings_buttons(user_id)
        )
        return True

    # 2. واجهة اختيار اللغة
    if data == "change_language":
        await event.edit(
            "🌐 **الرجاء اختيار اللغة المناسبة لك:**\n"
            "🌐 **Please choose your language:**",
            buttons=[
                [Button.inline("العربية 🇸🇦", data="set_language:ar"),
                 Button.inline("English 🇺🇸", data="set_language:en")],
                [Button.inline("فارسی 🇮🇷", data="set_language:fa"),
                 Button.inline("中文 🇨🇳", data="set_language:zh")],
                [Button.inline("Русский 🇷🇺", data="set_language:ru")],
                [Button.inline("🔙 رجوع", data="settings_menu")]
            ]
        )
        return True

    # 3. تنفيذ تغيير اللغة
    if data.startswith("set_language:"):
        lang_code = data.split(":")[1]
        lang.set_user_language(user_id, lang_code)

        confirm_msg = lang.get_message(user_id, 'LANGUAGE_CHANGED_MESSAGE')
        await cb(confirm_msg, alert=True)

        # العودة للمنيو الرئيسي بتعديل نفس الرسالة
        if render_main:
            await render_main(event)
        return True

    # 4. واجهة اختيار العملة
    if data == "change_currency":
        await event.edit(
            "💱 **اختر العملة المفضلة لعرض الأسعار:**",
            buttons=[
                [Button.inline("الريال السعودي (SAR)", data="set_currency:SAR")],
                [Button.inline("الريال اليمني (YER)", data="set_currency:YER")],
                [Button.inline("الدولار الأمريكي (USD)", data="set_currency:USD")],
                [Button.inline("🔙 رجوع", data="settings_menu")]
            ]
        )
        return True

    # 5. تنفيذ تغيير العملة
    if data.startswith("set_currency:"):
        currency = data.split(":")[1]
        user_data = db.get(f"user_{user_id}") or {"coins": 0, "id": user_id}
        user_data["currency"] = currency
        db.set(f"user_{user_id}", user_data)

        await cb(f"✅ تم تغيير العملة المفضلة إلى {currency}", alert=True)

        if render_main:
            await render_main(event)
        return True

    return False