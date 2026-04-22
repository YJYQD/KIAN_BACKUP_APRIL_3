from telethon import Button


async def handle_storage(event, user_id, data, **ctx):
    storage_manager = ctx["storage_manager"]
    lang_manager = ctx["lang_manager"]

    # 1. القائمة الرئيسية: اختيار القسم
    if data == "storage_menu":
        stats = storage_manager.get_storage_stats()
        msg = (
            "**📦 إدارة التخزين والتحكم بالمخزون**\n\n"
            f"• إجمالي الأرقام: `{stats['total']}`\n"
            "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
            "**📂 اختر القسم لإدارة أرقامه:**"
        )
        buttons = [
            [Button.inline(f"📞 العادي ({len(storage_manager.get_accounts_by_type('normal'))})",
                           data="view_stored:normal:0"),
             Button.inline(f"🎭 المزيف ({len(storage_manager.get_accounts_by_type('fake'))})",
                           data="view_stored:fake:0")],
            [Button.inline(f"⚠️ الاحتيالي ({len(storage_manager.get_accounts_by_type('fraud'))})",
                           data="view_stored:fraud:0"),
             Button.inline(f"📱 القديم ({len(storage_manager.get_accounts_by_type('old_creation'))})",
                           data="view_stored:old_creation:0")],
            [Button.inline("⚙️ إعدادات البيع التلقائي", data="auto_sell_settings")],
            [Button.inline("🔙 رجوع للأدمن", data="admin_panel")]
        ]
        await event.edit(msg, buttons=buttons)
        return True

    # 2. عرض الأرقام حسب القسم ونظام الصفحات
    if data.startswith("view_stored:"):
        # التنسيق: view_stored:القسم:الصفحة
        parts = data.split(":")
        section = parts[1]
        page = int(parts[2])

        # جلب أرقام هذا القسم فقط
        numbers = storage_manager.get_accounts_by_type(section)
        section_title = {"normal": "العادي", "fake": "المزيف", "fraud": "الاحتيالي",
                         "old_creation": "الإنشاء القديم"}.get(section, section)

        if not numbers:
            await event.edit(f"**📭 لا توجد أرقام في قسم ({section_title}) حالياً**",
                             buttons=[[Button.inline("🔙 رجوع", data="storage_menu")]])
            return True

        per_page = 10
        start = page * per_page
        end = start + per_page
        chunk = numbers[start:end]

        buttons = []
        for item in chunk:
            phone = item.get("phone_number")
            status = item.get("status", "stored")
            emoji = "🟢" if status == "selling" else "⚪"
            buttons.append([Button.inline(f"{emoji} +{phone} | {status}", data=f"manage_num:{phone}")])

        nav_buttons = []
        if page > 0:
            nav_buttons.append(Button.inline("⬅️ السابق", data=f"view_stored:{section}:{page - 1}"))
        if end < len(numbers):
            nav_buttons.append(Button.inline("التالي ➡️", data=f"view_stored:{section}:{page + 1}"))

        if nav_buttons: buttons.append(nav_buttons)
        buttons.append([Button.inline(f"📑 {section_title} | ص {page + 1}", data="ignore"),
                        Button.inline("🔙 رجوع", data="storage_menu")])

        await event.edit(f"**📦 أرقام قسم {section_title} ({len(numbers)})**", buttons=buttons)
        return True

    # 3. إدارة رقم محدد (تلقائياً يعرف القسم من الرقم)
    if data.startswith("manage_num:"):
        phone_number = data.split(":", 1)[1]
        num, section = storage_manager.get_number_by_phone(phone_number)

        if not num:
            await event.answer("❌ عذراً، الرقم غير موجود في أي قسم", alert=True)
            return True

        status = num.get("status", "stored")
        msg = (
            "**📱 إدارة الرقم**\n\n"
            f"• الرقم: `+{phone_number}`\n"
            f"• القسم: `{section}`\n"
            f"• الحالة: **{status}**\n"
            f"• السعر: `{num.get('price', 0)}` SAR"
        )

        sell_action_btn = Button.inline("➕ إضافة للبيع", data=f"storage_add_sell:{phone_number}")
        if status == "selling":
            sell_action_btn = Button.inline("➖ إزالة من البيع", data=f"storage_remove_sell:{phone_number}")

        buttons = [
            [Button.inline("📨 طلب كود التفعيل", data=f"storage_get_code:{phone_number}")],
            [sell_action_btn],
            [Button.inline("🗑 حذف نهائياً", data=f"storage_delete:{phone_number}")],
            [Button.inline("🔙 رجوع للقسم", data=f"view_stored:{section}:0")]
        ]
        await event.edit(msg, buttons=buttons)
        return True

    # 4. العمليات السريعة
    if data.startswith(("storage_add_sell:", "storage_remove_sell:", "storage_delete:")):
        action, phone = data.split(":")
        num, section = storage_manager.get_number_by_phone(phone)

        if "add" in action:
            storage_manager.update_number_status(phone, "selling")
            await event.answer("✅ تم عرض الرقم للبيع", alert=True)
        elif "remove" in action:
            storage_manager.update_number_status(phone, "stored")
            await event.answer("➖ تم إرجاع الرقم للمخزن", alert=True)
        elif "delete" in action:
            storage_manager.remove_number(phone)
            await event.answer("🗑 تم الحذف نهائياً", alert=True)
            return await handle_storage(event, user_id, f"view_stored:{section}:0", **ctx)

        return await handle_storage(event, user_id, f"manage_num:{phone}", **ctx)

    # 5. إعدادات البيع التلقائي
    if data == "auto_sell_settings":
        st = storage_manager.get_auto_sell_status()
        status_text = "✅ مفعل" if st.get("enabled") else "❌ معطل"
        msg = f"**⚙️ إعدادات البيع التلقائي**\n\nالحالة الحالية: **{status_text}**"
        buttons = [
            [Button.inline("✅ تفعيل", data="enable_auto_sell"), Button.inline("❌ تعطيل", data="disable_auto_sell")],
            [Button.inline("🔙 رجوع", data="storage_menu")]
        ]
        await event.edit(msg, buttons=buttons)
        return True

    if data == "enable_auto_sell":
        storage_manager.set_auto_sell(True)
        await event.answer("✅ تم تفعيل البيع التلقائي", alert=True)
        return await handle_storage(event, user_id, "auto_sell_settings", **ctx)

    if data == "disable_auto_sell":
        storage_manager.set_auto_sell(False)
        await event.answer("❌ تم إيقاف البيع التلقائي", alert=True)
        return await handle_storage(event, user_id, "auto_sell_settings", **ctx)

    # 6. جلب الكود
    if data.startswith("storage_get_code:"):
        phone = data.split(":")[1]
        await event.answer("⏳ جاري جلب الكود...", alert=False)
        try:
            from plugins.get_code import get_code
            code = await get_code(phone)
            if code:
                await event.respond(f"📩 الكود الأخير لـ `+{phone}`: **{code}**")
            else:
                await event.respond(f"❌ لم يتم العثور على كود لـ `+{phone}`")
        except Exception as e:
            await event.respond(f"❌ خطأ: {str(e)}")
        return True
    if data == "enable_auto_sell":
        storage_manager.set_auto_sell(True)
        await event.answer("✅ تم تفعيل البيع التلقائي!", alert=True)
        return await handle_storage(event, user_id, "auto_sell_settings", **ctx)

    if data == "disable_auto_sell":
        storage_manager.set_auto_sell(False)
        await event.answer("❌ تم إيقاف البيع التلقائي.", alert=True)
        return await handle_storage(event, user_id, "auto_sell_settings", **ctx)

    return False