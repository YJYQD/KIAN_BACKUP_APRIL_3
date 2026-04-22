from telethon import Button

async def handle_navigation(event, data, user_id, **ctx):
    # جلب دالة عرض القائمة الرئيسية من القاموس المرسل
    render_main_menu = ctx.get("render_main_menu")

    # 1. الرجوع للقائمة الرئيسية
    if data == "main":
        if render_main_menu:
            await render_main_menu(event)
        return True

    # 2. الرجوع لقسم الشراء (قائمة الأقسام الأربعة)
    if data == "back_to_buy_menu":
        # ابحث عن الدالة اللي تعرض قائمة الشراء للمستخدمين وعدل الأزرار كذا:
        buttons = [
            [Button.inline("📞 شراء رقم", data="buy_type:normal")],
            [Button.inline("🎭 ارقام مزيف", data="buy_type:fake")],
            [Button.inline("⚠️ ارقام احتيالي", data="buy_type:fraud")],
            [Button.inline("📱 حسابات إنشاء قديم", data="buy_type:old_creation")],
            [Button.inline("🔙 رجوع للقائمة الرئيسية", data="main_menu")]
        ]
        await event.edit("🛒 **اختر القسم المراد الشراء منه:**", buttons=buttons)
        return True

    # 3. الرجوع للوحة تحكم الأدمن
    if data == "back_to_admin_panel":
        try:
            from handlers.admin_handler import render_admin_panel
            await render_admin_panel(event, user_id)
        except ImportError:
            await event.answer("⚠️ خطأ: تعذر العثور على لوحة التحكم.", alert=True)
        return True

    return False