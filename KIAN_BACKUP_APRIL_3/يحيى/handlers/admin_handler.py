import os

from telethon import Button, TelegramClient
from telethon.errors import SessionPasswordNeededError


# دالة مساعدة لتعديل الرسالة أو الرد في حال فشل التعديل
async def safe_edit_or_reply(event, text, buttons=None):
    try:
        await event.edit(text, buttons=buttons)
    except:
        await event.respond(text, buttons=buttons)

async def render_admin_panel(event, user_id):
    """دالة مخصصة لإعادة عرض لوحة التحكم"""
    await safe_edit_or_reply(event, "🔧 **لوحة تحكم الأدمن - إدارة بوت كيان**", get_admin_panel_buttons(user_id))

def get_admin_panel_buttons(user_id):
    """توليد أزرار لوحة التحكم الرئيسية للأدمن"""
    return [
        [Button.inline("- إعدادات الأرقام 📂", data="admin_panel_numbers_settings")],
        [Button.inline("- الاشتراك الإجباري 〽️", data="ajxkho"),
         Button.inline("- قسم الأدمنية 👨‍✈️", data="aksgl")],
        [Button.inline("- قسم البيع و الشراء 💰", data="ajkofgl")],
        [Button.inline("- قسم الرصيد 💰", data="ajkcoingl"),
         Button.inline("- قسم الحظر 🚫", data="bbvjls")],
        [Button.inline("- قناة إثباتات التسليم 📡", data="set_trust_channel")],
        [Button.inline("- إعدادات العملات 💱", data="currency_settings")],
        [Button.inline("📦 التخزين", data="storage_menu")],
        [Button.inline("👥 عرض المستخدمين", data="show_users_list")],
        [Button.inline("- إذاعة للأعضاء 📢", data="broadcast")],
        [Button.inline("- تعديل رسالة القوانين 📜", data="edit_rules")],
        [Button.inline("- إضافة أرقام (عبر الكود) 📥", data="admin_type_add:normal")],
        [Button.inline("🎟️ إنشاء كود خصم", data="create_coupon_prompt")],
        [Button.inline("🌐 تغيير اللغة", data="change_language")],
        [Button.inline("🔙 رجوع للقائمة الرئيسية", data="main")]
    ]

async def handle_admin(event, user_id, data, db, **ctx):
    client = event.client

    # الاستيراد المحلي لمنع الـ Circular Import
    from main_enhanced import (
        ACCOUNT_TYPE_META, get_type_total, get_type_stock_rows, is_admin_user,
        API_ID, API_HASH, db_sections, storage_managers, SoldHandler, get_type_country_settings
    )
    from handlers.menu_handler import render_sell_buy_admin_menu, render_users_list, render_ban_menu

    # حماية اللوحة
    if not is_admin_user(user_id):
        return False

    # 1. لوحة التحكم الرئيسية
    if data == "admin_panel":
        await render_admin_panel(event, user_id)
        return True

    # 2. إحصائيات البيع والشراء
    if data == "ajkofgl":
        await render_sell_buy_admin_menu(event, user_id)
        return True

    # 3. عرض المستخدمين
    if data == "show_users_list":
        await render_users_list(event, user_id, db)
        return True

    # 4. اختيار قسم الأرقام
    if data == "admin_panel_numbers_settings":
        buttons = [
            [Button.inline("📞 شراء رقم", data="admin_view_type:normal"),
             Button.inline("🎭 ارقام مزيف", data="admin_view_type:fake")],
            [Button.inline("⚠️ ارقام احتيالي", data="admin_view_type:fraud"),
             Button.inline("📱 حسابات إنشاء قديم", data="admin_view_type:old_creation")],
            [Button.inline("🔙 رجوع", data="admin_panel")]
        ]
        await safe_edit_or_reply(event, "📁 **اختر القسم المراد إدارته:**", buttons=buttons)
        return True

    # 5. واجهة القسم المختار
    if data.startswith("admin_view_type:"):
        account_type = data.split(":")[1]
        total = get_type_total(account_type)
        buttons = [
            [Button.inline("➕ إضافة رقم", data=f"admin_type_add:{account_type}"),
             Button.inline("🗑 حذف رقم", data=f"admin_type_delete:{account_type}")],
            [Button.inline("🌍 إضافة دولة", data=f"admin_type_country_add:{account_type}"),
             Button.inline("🗑 حذف دولة", data=f"admin_type_country_delete:{account_type}")],
            [Button.inline("📊 عرض الإجمالي", data=f"admin_type_inventory:{account_type}")],
            [Button.inline("⦉ رجوع ⦊", data="admin_panel_numbers_settings")]
        ]
        await event.edit(
            f"**{ACCOUNT_TYPE_META[account_type]['emoji']} إعدادات {ACCOUNT_TYPE_META[account_type]['title']}**\n\nإجمالي المتاح: {total}",
            buttons=buttons)
        return True

    # 6. إضافة دولة
    if data.startswith("admin_type_country_add:"):
        account_type = data.split(":")[1]
        async with client.conversation(user_id, timeout=300) as conv:
            await conv.send_message("🌍 **أرسل اسم الدولة (مثلاً: السعودية):**")
            name = (await conv.get_response()).text.strip()
            await conv.send_message(f"🔢 **أرسل رمز نداء {name} (مثال: 966):**")
            code = (await conv.get_response()).text.strip().replace('+', '')
            await conv.send_message(f"💰 **أرسل سعر الرقم لـ {name}:**")
            try:
                price = float((await conv.get_response()).text.strip())
                if account_type == "normal":
                    countries = db_sections["normal"].get("countries") or []
                    countries.append({"name": name, "calling_code": code, "price": price})
                    db_sections["normal"].set("countries", countries)
                else:
                    meta = ACCOUNT_TYPE_META[account_type]
                    settings = db_sections[account_type].get(meta["countries_key"]) or {}
                    settings[name] = {"calling_code": code, "price": price}
                    db_sections[account_type].set(meta["countries_key"], settings)
                await conv.send_message(f"✅ تم إضافة {name} بنجاح.")
            except:
                await conv.send_message("❌ فشل: السعر غير صحيح.")
        return True

    # 7. حذف دولة
    if data.startswith("admin_type_country_delete:"):
        account_type = data.split(":")[1]
        if account_type == "normal":
            countries = db_sections["normal"].get("countries") or []
            country_names = [c['name'] for c in countries]
        else:
            meta = ACCOUNT_TYPE_META[account_type]
            settings = db_sections[account_type].get(meta["countries_key"]) or {}
            country_names = list(settings.keys())

        if not country_names:
            await event.answer("⚠️ لا توجد دول مضافة في هذا القسم.", alert=True)
            return True

        buttons = []
        for i in range(0, len(country_names), 2):
            row = [Button.inline(f"❌ {name}", data=f"conf_del_c:{account_type}:{name}") for name in country_names[i:i + 2]]
            buttons.append(row)
        buttons.append([Button.inline("⦉ رجوع ⦊", data=f"admin_view_type:{account_type}")])
        await event.edit(f"🌍 **اختر الدولة المراد حذفها من قسم {account_type}:**", buttons=buttons)
        return True

    # 8. تنفيذ حذف الدولة
    if data.startswith("conf_del_c:"):
        _, account_type, country_name = data.split(":")
        if account_type == "normal":
            countries = db_sections["normal"].get("countries") or []
            new_countries = [c for c in countries if c['name'] != country_name]
            db_sections["normal"].set("countries", new_countries)
        else:
            meta = ACCOUNT_TYPE_META[account_type]
            settings = db_sections[account_type].get(meta["countries_key"]) or {}
            if country_name in settings:
                del settings[country_name]
                db_sections[account_type].set(meta["countries_key"], settings)
        await event.answer(f"✅ تم حذف {country_name} بنجاح.", alert=True)
        return await handle_admin(event, user_id, f"admin_type_country_delete:{account_type}", db, **ctx)

        # 9. واجهة اختيار الدولة لإضافة رقم (نظام الأزرار)
    if data.startswith("admin_type_add:"):
            account_type = data.split(":")[1]
            countries_dict = get_type_country_settings(account_type)
            country_names = list(countries_dict.keys())

            if not country_names:
                await event.answer("⚠️ لا توجد دول مضافة في هذا القسم. أضف دولة أولاً.", alert=True)
                return True

            buttons = []
            for i in range(0, len(country_names), 2):
                row = [Button.inline(name, data=f"start_otp_add:{account_type}:{name}") for name in
                       country_names[i:i + 2]]
                buttons.append(row)
            buttons.append([Button.inline("⦉ رجوع ⦊", data=f"admin_view_type:{account_type}")])

            await event.edit(
                f"🌍 **قسم {ACCOUNT_TYPE_META[account_type]['title']}:**\nاختر الدولة التي ينتمي لها الرقم:",
                buttons=buttons)
            return True

        # 10. معالج بدء إضافة الرقم (OTP) بعد اختيار الدولة من الزر
    if data.startswith("start_otp_add:"):
            _, account_type, country_name = data.split(":")
            async with client.conversation(user_id, timeout=600) as conv:
                await conv.send_message(
                    f"📱 **إضافة رقم لـ {country_name}:**\nأرسل الرقم الآن مع رمز الدولة (مثال: 96650...)")
                phone = (await conv.get_response()).text.strip().replace('+', '').replace(' ', '')
                await conv.send_message(f"⏳ جاري طلب الكود للرقم {phone}...")
                os.makedirs('database/sessions', exist_ok=True)
                temp_session_path = f"database/sessions/{phone}"
                temp_client = TelegramClient(temp_session_path, int(API_ID), API_HASH)
                try:
                    await temp_client.connect()
                    await temp_client.send_code_request(phone)
                    await conv.send_message("📥 **أرسل كود التحقق الآن:**")
                    otp_code = (await conv.get_response()).text.strip()
                    try:
                        await temp_client.sign_in(phone, otp_code)
                    except SessionPasswordNeededError:
                        await conv.send_message("🔐 **أرسل كلمة السر (التحقق بخطوتين):**")
                        password_2fa = (await conv.get_response()).text.strip()
                        await temp_client.sign_in(password=password_2fa)

                    storage_managers[account_type].add_account(account_type, {
                        "phone_number": phone,
                        "session_path": f"{temp_session_path}.session",
                        "country": country_name,
                        "status": "stored"
                    })
                    await temp_client.disconnect()
                    await conv.send_message(f"✅ تم إضافة الرقم {phone} بنجاح!")
                except Exception as e:
                    await conv.send_message(f"❌ فشل: {str(e)}")
                    if temp_client.is_connected(): await temp_client.disconnect()
            return True
    # 10. حذف رقم
    if data.startswith("admin_type_delete:"):
        account_type = data.split(":")[1]
        async with client.conversation(user_id, timeout=300) as conv:
            await conv.send_message("📱 **أرسل رقم الهاتف المراد حذفه:**")
            phone = (await conv.get_response()).text.strip()
            if storage_managers[account_type].remove_number(phone):
                await conv.send_message(f"✅ تم حذف الرقم {phone} بنجاح.")
            else:
                await conv.send_message("❌ الرقم غير موجود.")
        return True

    # 11. إحصائيات المخزون
    if data.startswith("admin_type_inventory:"):
        account_type = data.split(":")[1]
        rows = get_type_stock_rows(account_type)
        if not rows:
            await event.answer("❌ لا يوجد مخزون.", alert=True)
            return True
        text = f"📊 **إحصائيات {ACCOUNT_TYPE_META[account_type]['title']}:**\n\n"
        for r in rows:
            text += f"🏳️ {r['country']} (+{r['calling_code']}): {r['count']} رقم | {r['price']} ﷼\n"
        await event.respond(text)
        return True

    # 12. إدارة الرصيد
    # 12. واجهة إدارة الرصيد (الخطوة 1: اختيار العملية)
    if data == "ajkcoingl":
        buttons = [
            [Button.inline("➕ إضافة رصيد", data="bal_step:add"),
             Button.inline("➖ خصم رصيد", data="bal_step:sub")],
            [Button.inline("🔙 رجوع", data="admin_panel")]
        ]
        await event.edit("💰 **إدارة ميزانية الأعضاء**\n\nاختر نوع العملية التي تريد القيام بها:", buttons=buttons)
        return True

     # معالجة خطوات الرصيد (آيدي ثم مبلغ)
    if data.startswith("bal_step:"):
            action = data.split(":")[1]
            action_text = "إضافة إلى" if action == "add" else "خصم من"

            async with client.conversation(user_id, timeout=300) as conv:
                # الخطوة 2: طلب الآيدي
                await conv.send_message(f"👤 **يرجى إرسال آيدي المستخدم المراد {action_text} رصيده:**")
                tid_msg = await conv.get_response()
                tid = tid_msg.text.strip()
                user_key = f"user_{tid}"

                if not db.exists(user_key):
                    await conv.send_message("❌ **هذا المستخدم غير موجود في قاعدة البيانات.**")
                    return True

                u_data = db.get(user_key)
                current_bal = u_data.get("coins", 0)
                username = u_data.get("username", "بدون يوزر")

                # الخطوة 3: طلب المبلغ مع عرض الحالة الحالية
                await conv.send_message(
                    f"👤 العضو: @{username} (`{tid}`)\n"
                    f"💰 الرصيد الحالي: `{current_bal:,.2f}` ﷼\n\n"
                    f"💵 **أرسل المبلغ المراد {action_text} حسابه:**"
                )

                amt_msg = await conv.get_response()
                try:
                    amt = float(amt_msg.text.strip())
                    if action == "add":
                        u_data["coins"] = current_bal + amt
                        msg_type = "إيداع"
                    else:
                        u_data["coins"] = max(0, current_bal - amt)
                        msg_type = "سحب"

                    db.set(user_key, u_data)

                    # تأكيد للأدمن
                    final_bal = u_data["coins"]
                    await conv.send_message(
                        f"✅ **تمت العملية بنجاح**\n"
                        f"🔹 النوع: {msg_type}\n"
                        f"🔹 العضو: `{tid}`\n"
                        f"🔹 المبلغ: `{amt}` ﷼\n"
                        f"💰 الرصيد الجديد: `{final_bal:,.2f}` ﷼"
                    )

                    # إشعار المستخدم تلقائياً
                    try:
                        notify_msg = (
                            f"🔔 **إشعار تحديث رصيد**\n\n"
                            f"تم {action_text} حسابك مبلغ: `{amt}` ﷼\n"
                            f"رصيدك الحالي هو: `{final_bal:,.2f}` ﷼"
                        )
                        await client.send_message(int(tid), notify_msg)
                    except:
                        pass  # في حال كان المستخدم حاظر البوت

                except ValueError:
                    await conv.send_message("❌ **خطأ: يجب إرسال أرقام فقط للمبلغ.**")
            return True

    # 13. الإذاعة
    if data == "broadcast":
        async with client.conversation(user_id, timeout=600) as conv:
            await conv.send_message("📢 **أرسل رسالة الإذاعة:**")
            msg = await conv.get_response()
            users = db.keys('user_%')
            await conv.send_message(f"⏳ جاري الإرسال لـ {len(users)} عضو...")
            count = 0
            for u in users:
                try:
                    await client.send_message(int(u.split('_')[1]), msg); count += 1
                except: continue
            await conv.send_message(f"✅ وصلت لـ {count} مستخدم.")
        return True

        # معالجة خطوات الحظر (إضافة/حذف/عرض)
    if data.startswith("ban_step:"):
            action = data.split(":")[1]

            # 1. عرض قائمة المحظورين
            if action == "list":
                bans = db.get("bad_guys") or []
                if not bans:
                    await event.answer("⚠️ لا يوجد أي مستخدم محظور حالياً.", alert=True)
                    return True
                msg = "📜 **قائمة المحظورين (IDs):**\n\n" + "\n".join([f"• `{uid}`" for uid in bans])
                await event.respond(msg)
                return True

            # 2. طلب الآيدي للحظر أو فكه
            action_text = "حظر" if action == "add" else "فك حظر"
            async with client.conversation(user_id, timeout=300) as conv:
                await conv.send_message(f"👤 **يرجى إرسال آيدي المستخدم المراد {action_text}ه:**")
                tid_msg = await conv.get_response()
                tid = tid_msg.text.strip()

                if not tid.isdigit():
                    await conv.send_message("❌ **خطأ: يجب إرسال الآيدي كأرقام فقط.**")
                    return True

                bans = db.get("bad_guys") or []

                if action == "add":
                    if tid in bans:
                        await conv.send_message("⚠️ **هذا المستخدم محظور بالفعل.**")
                    else:
                        bans.append(tid)
                        db.set("bad_guys", bans)
                        await conv.send_message(f"✅ تم حظر المستخدم `{tid}` بنجاح.")
                        # إشعار المستخدم (اختياري)
                        try:
                            await client.send_message(int(tid), "🚫 **إشعار إداري:** تم حظرك من استخدام البوت.")
                        except:
                            pass
                else:
                    if tid not in bans:
                        await conv.send_message("⚠️ **هذا المستخدم غير موجود في القائمة السوداء.**")
                    else:
                        bans.remove(tid)
                        db.set("bad_guys", bans)
                        await conv.send_message(f"✅ تم فك الحظر عن `{tid}` بنجاح.")
                        try:
                            await client.send_message(int(tid),
                                                      "✅ **إشعار إداري:** تم فك الحظر عنك، يمكنك استخدام البوت الآن.")
                        except:
                            pass
            return True
    # 15. قناة الإثباتات وقناة القوانين
    if data == "set_trust_channel":
        async with client.conversation(user_id, timeout=200) as conv:
            await conv.send_message("**📡 أرسل معرف القناة مع الـ @:**")
            res = (await conv.get_response()).text.strip()
            db.set("trust_channel", res); await conv.send_message(f"✅ تم التعيين.")
        return True

    if data == "edit_rules":
        async with client.conversation(user_id, timeout=300) as conv:
            await conv.send_message("**📜 أرسل نص القوانين الجديد:**")
            res = (await conv.get_response()).text.strip()
            db.set("bot_rules", res); await conv.send_message("✅ تم التحديث.")
        return True

    # 17. نظام الأكواد والعملات
    if data == "create_coupon_prompt":
        async with client.conversation(user_id, timeout=600) as conv:
            await conv.send_message("🎟️ **أرسل اسم الكود:**"); c_name = (await conv.get_response()).text.strip().upper()
            await conv.send_message(f"📊 **أرسل نسبة الخصم لـ `{c_name}`:**")
            try:
                c_per = float((await conv.get_response()).text.strip())
                await conv.send_message("👥 **أرسل عدد مرات الاستخدام:**"); c_max = int((await conv.get_response()).text.strip())
                coupons = db.get("discount_codes") or {}
                coupons[c_name] = {"percent": c_per, "max_uses": c_max, "current_uses": 0}
                db.set("discount_codes", coupons); await conv.send_message("✅ تم الإنشاء.")
            except: await conv.send_message("❌ خطأ.")
        return True

    if data == "currency_settings":
        async with client.conversation(user_id, timeout=200) as conv:
            await conv.send_message("**💱 أرسل سعر صرف الدولار مقابل الريال:**")
            try:
                usd_rate = float((await conv.get_response()).text.strip())
                rates = db.get("currency_rates") or {"SAR": 1.0, "YER": 66.67, "USD": 0.267}
                rates["USD"] = 1 / usd_rate; db.set("currency_rates", rates); await conv.send_message("✅ تم التحديث.")
            except: await conv.send_message("❌ خطأ.")
        return True

    # 19. الاشتراك الإجباري
    if data == "ajxkho":
        force = db.get("force") or []
        msg = "**〽️ القنوات الحالية:**\n" + "\n".join([f"• @{ch}" for ch in force])
        await event.edit(msg, buttons=[[Button.inline("➕ إضافة", data="add_force_channel"), Button.inline("🗑 حذف", data="del_force_channel")], [Button.inline("🔙 رجوع", data="admin_panel")]])
        return True

    if data == "add_force_channel":
        async with client.conversation(user_id, timeout=200) as conv:
            await conv.send_message("**📡 أرسل المعرف بدون @:**")
            res = (await conv.get_response()).text.strip().replace('@', '')
            f = db.get("force") or []; f.append(res); db.set("force", f); await conv.send_message(f"✅ تمت إضافة @{res}")
        return True

    if data == "del_force_channel":
        async with client.conversation(user_id, timeout=200) as conv:
            await conv.send_message("**🗑 أرسل المعرف لحذفه:**")
            res = (await conv.get_response()).text.strip().replace('@', '')
            f = db.get("force") or []
            if res in f: f.remove(res); db.set("force", f); await conv.send_message("✅ تم الحذف.")
        return True

    # 20. قسم الأدمنية
    if data == "aksgl":
        admins = db.get("admins") or []
        msg = "**👨‍✈️ المشرفين:**\n" + "\n".join([f"• `{adm}`" for adm in admins])
        await event.edit(msg, buttons=[[Button.inline("➕ إضافة", data="add_admin_prompt"), Button.inline("🗑 حذف", data="del_admin_prompt")], [Button.inline("🔙 رجوع", data="admin_panel")]])
        return True

    if data == "add_admin_prompt":
        async with client.conversation(user_id, timeout=200) as conv:
            await conv.send_message("**👤 أرسل آيدي الأدمن:**")
            try:
                new_id = int((await conv.get_response()).text.strip())
                a = db.get("admins") or []; a.append(new_id); db.set("admins", a); await conv.send_message("✅ تمت الإضافة.")
            except: await conv.send_message("❌ خطأ.")
        return True

    if data == "del_admin_prompt":
        async with client.conversation(user_id, timeout=200) as conv:
            await conv.send_message("**🗑 أرسل آيدي الأدمن لحذفه:**")
            try:
                del_id = int((await conv.get_response()).text.strip())
                a = db.get("admins") or []
                if del_id in a: a.remove(del_id); db.set("admins", a); await conv.send_message("✅ تم الحذف.")
            except: await conv.send_message("❌ خطأ.")
        return True

    # زر التخزين وتغيير اللغة
        # زر التخزين
    if data == "storage_menu":
        from handlers.storage_handler import handle_storage
        await handle_storage(event, user_id, data, **ctx)
        return True

    if data == "change_language":
        from handlers.settings_handler import handle_settings
        return await handle_settings(event, user_id, "change_language", db=db, lang_manager=None)

    # معالجة صفحات قائمة المستخدمين
    if data.startswith("users_page:"):
        await render_users_list(event, user_id, db, page=int(data.split(":")[1]))
        return True

    # إحصائيات المبيعات
    if data == "sales_stats":
        from invoice_system import InvoiceSystem
        stats = InvoiceSystem(db).get_overall_stats()
        msg = (
            "📊 **إحصائيات المبيعات العامة:**\n\n"
            f"💰 إجمالي الأرباح: {stats.get('total_revenue', 0)} SAR\n"
            f"✅ طلبات ناجحة: {stats.get('successful_orders', 0)}\n"
            f"❌ طلبات ملغاة: {stats.get('cancelled_orders', 0)}"
        )
        await event.respond(msg)
        return True

    return False