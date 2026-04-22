from telethon import Button


# 1. قائمة اختيار الأقسام الأربعة للأدمن
def get_admin_sections_menu():
    """توليد قائمة الأقسام الرئيسية لإدارة الحسابات"""
    return [
        [Button.inline("📞 شراء رقم ", data="admin_view_type:normal")],
        [Button.inline("🎭 ارقام مزيف", data="admin_view_type:fake")],
        [Button.inline("⚠️ ارقام احتيالي", data="admin_view_type:fraud")],
        [Button.inline("📱 حسابات إنشاء قديم", data="admin_view_type:old_creation")],
        [Button.inline("🎟️ إنشاء كود خصم", data="create_coupon_prompt")],
        [Button.inline("⦉ رجوع للوحة التحكم ⦊", data="admin_panel")]
    ]


# 2. أزرار التحكم داخل القسم المختار
def get_specific_management_buttons(account_type):
    """أزرار العمليات (إضافة/حذف/عرض) لقسم معين"""
    return [
        [Button.inline("➕ إضافة رقم", data=f"admin_type_add:{account_type}"),
         Button.inline("🗑 حذف رقم", data=f"admin_type_delete:{account_type}")],
        [Button.inline("🌍 إضافة دولة", data=f"admin_type_country_add:{account_type}"),
         Button.inline("🗑 حذف دولة", data=f"admin_type_country_delete:{account_type}")],
        [Button.inline("📊 عرض المخزون", data=f"admin_type_inventory:{account_type}")],
        [Button.inline("⦉ رجوع للأقسام ⦊", data="admin_panel_numbers_settings")]
    ]


# 3. واجهة قسم البيع والشراء للأدمن
async def render_sell_buy_admin_menu(event, user_id):
    """عرض إحصائيات المبيعات والطلبات"""
    buttons = [
        [Button.inline("📊 إحصائيات المبيعات", data="sales_stats")],
        [Button.inline("📑 قائمة الطلبات", data="orders_list")],
        [Button.inline("🔙 رجوع", data="admin_panel")]
    ]
    await event.edit("**💰 قسم إدارة البيع والشراء**\n\nيمكنك متابعة العمليات المالية وإحصائيات المتجر هنا:",
                     buttons=buttons)


# 4. واجهة إدارة الرصيد للأدمن
async def render_balance_menu(event, user_id):
    """أزرار التحكم في أرصدة المستخدمين"""
    buttons = [
        [Button.inline("➕ إضافة رصيد", data="balance_add"),
         Button.inline("➖ خصم رصيد", data="balance_sub")],
        [Button.inline("🔙 رجوع", data="admin_panel")]
    ]
    await event.edit("**💰 قسم إدارة رصيد الأعضاء**\n\nاختر العملية المطلوبة للتحكم في رصيد مستخدم معين:",
                     buttons=buttons)


# واجهة إدارة الحظر
async def render_ban_menu(event, user_id, db):
    """عرض حالة الحظر وأزرار التحكم بنظام الخطوات"""
    bans = db.get("bad_guys") or []
    msg = (
        "🚫 **مركز إدارة الحظر والوصول**\n\n"
        f"👤 عدد المحظورين حالياً: `{len(bans)}` عضو\n\n"
        "• **حظر عضو:** لمنعه من استخدام كافة ميزات البوت.\n"
        "• **فك حظر:** لإعادة صلاحية الوصول للمستخدم.\n"
        "• **عرض القائمة:** لمراجعة المعرفات المحظورة."
    )
    buttons = [
        [Button.inline("🚫 حظر مستخدم", data="ban_step:add"),
         Button.inline("✅ فك حظر", data="ban_step:remove")],
        [Button.inline("📜 عرض قائمة الحظر", data="ban_step:list")],
        [Button.inline("🔙 رجوع للوحة الأدمن", data="admin_panel")]
    ]
    await event.edit(msg, buttons=buttons)


# 6. واجهة عرض المستخدمين بنظام الصفحات
async def render_users_list(event, user_id, db, page=0):
    """عرض قائمة المستخدمين مع دعم التنقل بين الصفحات"""
    user_keys = db.keys('user_%')
    total_users = len(user_keys)
    per_page = 10
    total_pages = (total_users + per_page - 1) // per_page

    start_idx = page * per_page
    end_idx = start_idx + per_page

    current_page_keys = user_keys[start_idx:end_idx]

    msg = f"👥 **إحصائيات الأعضاء ({total_users})**\n"
    msg += f"📄 صفحة: {page + 1} من {total_pages}\n\n"

    if not current_page_keys:
        msg += "⚠️ لا يوجد مستخدمين لعرضهم في هذه الصفحة."
    else:
        for key in current_page_keys:
            u_data = db.get(key)
            u_id = key.split('_')[1]
            u_name = u_data.get('username', 'لا يوجد')
            u_coins = u_data.get('coins', 0)
            msg += f"👤 `{u_id}` | @{u_name} | 💰 {u_coins:.1f}\n"

    buttons = []
    # صف أزرار التنقل
    nav_row = []
    if page > 0:
        nav_row.append(Button.inline("⬅️ السابق", data=f"users_page:{page - 1}"))
    if end_idx < total_users:
        nav_row.append(Button.inline("التالي ➡️", data=f"users_page:{page + 1}"))

    if nav_row:
        buttons.append(nav_row)

    buttons.append([Button.inline("🔙 رجوع للوحة الأدمن", data="admin_panel")])

    try:
        await event.edit(msg, buttons=buttons)
    except Exception:
        # في حال كان النص طويلاً جداً أو لم يتم التعديل
        await event.respond(msg, buttons=buttons)