from telethon import Button


async def handle_referral(event, user_id, data, **ctx):
    db = ctx["db"]
    lang_manager = ctx["lang_manager"]
    referral_system = ctx["referral_system"]  # جلب نظام الإحالة من السياق

    # 1. القائمة الرئيسية لنظام الإحالة
    if data == "referral_system":
        stats = referral_system.get_referral_stats(user_id)
        reward = referral_system.get_referral_reward()

        # جلب الرسالة المترجمة التي تعرض المكافأة والإحصائيات
        msg = lang_manager.get_message(
            user_id,
            'REFERRAL_MENU_MESSAGE',
            reward=reward,
            total_referred=stats.get('total_referred', 0),
            total_earned=stats.get('total_earned', 0)
        )

        buttons = [
            [Button.inline("🔗 رابط الدعوة الخاص بي", data="show_referral_link")],
            [Button.inline("📊 إحصائياتي التفصيلية", data="show_referral_stats")],
            [Button.inline(lang_manager.get_message(user_id, 'BACK_BUTTON'), data="main")]
        ]

        await event.edit(msg, buttons=buttons)
        return True

    # 2. عرض رابط الدعوة
    if data == "show_referral_link":
        code = referral_system.get_referral_code(user_id)
        me = await event.client.get_me()
        link = f"https://t.me/{me.username}?start={code}"

        msg = lang_manager.get_message(
            user_id,
            'REFERRAL_LINK_MESSAGE',
            link=link,
            reward=referral_system.get_referral_reward()
        )

        buttons = [
            [Button.url("مشاركة الرابط 📤",
                        f"https://t.me/share/url?url={link}&text=اشترك في أفضل بوت لبيع الأرقام والحسابات!")],
            [Button.inline(lang_manager.get_message(user_id, 'BACK_BUTTON'), data="referral_system")]
        ]

        await event.edit(msg, buttons=buttons)
        return True

    # 3. عرض الإحصائيات
    if data == "show_referral_stats":
        stats = referral_system.get_referral_stats(user_id)
        reward = referral_system.get_referral_reward()

        msg = lang_manager.get_message(
            user_id,
            'REFERRAL_STATS_MESSAGE',
            total_referred=stats.get('total_referred', 0),
            total_earned=stats.get('total_earned', 0),
            reward=reward
        )

        await event.edit(msg, buttons=[
            [Button.inline(lang_manager.get_message(user_id, 'BACK_BUTTON'), data="referral_system")]])
        return True

    return False