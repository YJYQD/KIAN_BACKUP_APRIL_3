from telethon import Button
import asyncio


async def handle_balance(event, user_id, data, db):
    # تم توحيد الـ Data لتتوافق مع زر لوحة الأدمن (ajkcoingl)
    if data in ["balance_menu", "ajkcoingl"]:
        await event.edit(
            "**💰 قسم إدارة رصيد الأعضاء**\n\nاختر العملية المطلوبة:",
            buttons=[
                [Button.inline("➕ إضافة رصيد", data="balance_add"),
                 Button.inline("➖ خصم رصيد", data="balance_sub")],
                [Button.inline("🔍 استعلام عن رصيد", data="balance_view")],
                [Button.inline("⦉ رجوع ⦊", data="admin_panel")]
            ]
        )
        return True

    # 1. إضافة رصيد
    if data == "balance_add":
        async with event.client.conversation(user_id, timeout=60) as conv:
            await conv.send_message("➕ **إضافة رصيد**\nأرسل آيدي العضو ثم مسافة ثم المبلغ:\nمثال: `1234567 10`")
            try:
                msg = await conv.get_response()
                parts = msg.text.split()
                if len(parts) < 2: raise ValueError

                target_uid, amount = parts[0], float(parts[1])
                user_key = f"user_{target_uid}"

                if not db.exists(user_key):
                    await conv.send_message("❌ هذا العضو غير مسجل في البوت.")
                    return True

                user_data = db.get(user_key)
                user_data["coins"] = user_data.get("coins", 0) + amount
                db.set(user_key, user_data)

                await conv.send_message(f"✅ تم إضافة {amount} ﷼ بنجاح.\nالرصيد الحالي: {user_data['coins']} ﷼")

                # إشعار العضو
                try:
                    await event.client.send_message(int(target_uid), f"💰 تم إضافة {amount} ﷼ لرصيدك من قبل الإدارة.")
                except:
                    pass

            except:
                await conv.send_message("❌ خطأ! يرجى إرسال (الآيدي مسافة المبلغ) بشكل صحيح.")
        return True

    # 2. خصم رصيد
    if data == "balance_sub":
        async with event.client.conversation(user_id, timeout=60) as conv:
            await conv.send_message("➖ **خصم رصيد**\nأرسل آيدي العضو ثم مسافة ثم المبلغ المراد خصمه:")
            try:
                msg = await conv.get_response()
                parts = msg.text.split()
                if len(parts) < 2: raise ValueError

                target_uid, amount = parts[0], float(parts[1])
                user_key = f"user_{target_uid}"

                if not db.exists(user_key):
                    await conv.send_message("❌ العضو غير موجود.")
                    return True

                user_data = db.get(user_key)
                user_data["coins"] = user_data.get("coins", 0) - amount
                db.set(user_key, user_data)

                await conv.send_message(f"✅ تم الخصم بنجاح.\nالرصيد المتبقي: {user_data['coins']} ﷼")
            except:
                await conv.send_message("❌ خطأ في الإدخال.")
        return True

    # 3. استعلام عن رصيد (إضافة جديدة)
    if data == "balance_view":
        async with event.client.conversation(user_id, timeout=60) as conv:
            await conv.send_message("🔍 **استعلام عن رصيد**\nأرسل آيدي العضو الآن:")
            try:
                msg = await conv.get_response()
                target_uid = msg.text.strip()
                user_key = f"user_{target_uid}"

                if not db.exists(user_key):
                    await conv.send_message("❌ العضو غير موجود.")
                    return True

                balance = db.get(user_key).get("coins", 0)
                await conv.send_message(f"👤 العضو: `{target_uid}`\n💰 رصيده الحالي: {balance:.2f} ﷼")
            except:
                await conv.send_message("❌ آيدي غير صالح.")
        return True

    return False