from telethon import Button
from handlers.menu_handler import get_admin_sections_menu, get_specific_management_buttons

# قواميس لتخزين حالات الأدمن (ماذا ينتظر البوت من الأدمن حالياً)
user_add_states = {}
user_delete_states = {}
country_add_states = {}
country_delete_states = {}


async def handle_numbers(event, user_id, data):
    client = event.client

    # ==========================================
    # 1. فتح قائمة الأقسام (عادي، مزيف، إلخ)
    # ==========================================
    if data == "admin_panel_numbers_settings":
        await event.edit(
            "**🗄 إدارة مخزون الأقسام:**\nاختر القسم الذي تريد إدارته حالياً:",
            buttons=get_admin_sections_menu()
        )
        return True

    # ==========================================
    # 2. واجهة التحكم بالقسم المختار
    # ==========================================
    if data.startswith("manage_section:"):
        account_type = data.split(":")[1]
        titles = {"normal": "العادية", "fake": "المزيفة", "fraud": "الاحتيالية", "old_creation": "القديمة"}

        await event.edit(
            f"**⚙️ إدارة قسم أرقام: {titles.get(account_type, account_type)}**",
            buttons=get_specific_management_buttons(account_type)
        )
        return True

    # ==========================================
    # 3. إدارة الأرقام (إضافة / حذف)
    # ==========================================
    if data.startswith("admin_type_add:"):  # تم توحيد الاسم مع main_enhanced
        account_type = data.split(":")[1]
        user_add_states[user_id] = account_type
        await event.reply(f"📥 **قسم {account_type}**\nأرسل الرقم مع المفتاح الدولي (مثال: `+9665xxxxxxx`) لبرمجته:")
        return True

    if data.startswith("admin_type_delete:"):
        account_type = data.split(":")[1]
        user_delete_states[user_id] = account_type
        await event.reply(f"🗑 **قسم {account_type}**\nأرسل الرقم بدون (+) لحذفه نهائياً من المخزن:")
        return True

    # ==========================================
    # 4. إدارة الدول (إضافة / حذف) - ميزة جديدة
    # ==========================================
    if data.startswith("admin_type_country_add:"):
        account_type = data.split(":")[1]
        country_add_states[user_id] = account_type
        await event.reply(
            f"🌍 **إضافة دولة لـ {account_type}**\nأرسل بيانات الدولة بهذا التنسيق:\n`اسم الدولة - المفتاح - السعر`\n\nمثال: `السعودية - 966 - 15`")
        return True

    if data.startswith("admin_type_country_delete:"):
        account_type = data.split(":")[1]
        country_delete_states[user_id] = account_type
        await event.reply(f"🗑 **حذف دولة من {account_type}**\nأرسل اسم الدولة لحذفها وحذف كافة أرقامها:")
        return True

    # ==========================================
    # 5. عرض المخزون التفصيلي
    # ==========================================
    if data.startswith("admin_type_inventory:"):
        account_type = data.split(":")[1]
        # الاستدعاء من الملف التشغيلي الحالي
        from main_enhanced import get_type_stock_rows

        rows = get_type_stock_rows(account_type)
        if not rows:
            await event.reply(f"❌ لا يوجد مخزون مضاف في قسم {account_type} حتى الآن.")
            return True

        text = f"📊 **إحصائيات مخزن {account_type}:**\n\n"
        for row in rows:
            text += f"🏳️ {row['country']} (+{row['calling_code']})\n"
            text += f"💰 السعر: {row['price']} ﷼ | 📦 المتوفر: {row['count']} رقم\n"
            text += f"────────────────\n"

        await event.reply(text)
        return True

    return False