from telethon import Button
import asyncio


async def handle_transfer(event, user_id, data, **ctx):
    db = ctx["db"]
    lang_manager = ctx["lang_manager"]
    get_formatted_currency = ctx["get_formatted_currency"]  # دالة تنسيق العملات

    # 1. الدخول لقسم التحويل
    if data == "transfer":
        msg = lang_manager.get_message(user_id, 'TRANSFER_MESSAGE')
        buttons = [[Button.inline(lang_manager.get_message(user_id, 'BACK_BUTTON'), data="main")]]

        async with event.client.conversation(user_id, timeout=120) as conv:
            await event.edit(msg, buttons=buttons)

            # الخطوة الأولى: استقبال آيدي المستلم
            try:
                id_msg = await conv.get_response()
                target_id = int(id_msg.text.strip())

                if target_id == user_id:
                    await conv.send_message("⚠️ لا يمكنك التحويل لنفسك!")
                    return True

                if not db.exists(f"user_{target_id}"):
                    await conv.send_message("❌ هذا الآيدي غير مسجل في البوت.")
                    return True

                # الخطوة الثانية: استقبال المبلغ
                await conv.send_message("💰 **أرسل الآن المبلغ المراد تحويله (بالريال السعودي):**")
                amount_msg = await conv.get_response()
                amount = float(amount_msg.text.strip())

                if amount <= 0:
                    await conv.send_message("❌ يجب أن يكون المبلغ أكبر من صفر.")
                    return True

                # الخطوة الثالثة: التحقق من الرصيد والعمولة (2%)
                commission = amount * 0.02
                total_required = amount + commission

                sender_data = db.get(f"user_{user_id}")
                if sender_data["coins"] < total_required:
                    needed = get_formatted_currency(user_id, total_required)
                    await conv.send_message(f"❌ رصيدك غير كافٍ. المبلغ المطلوب مع العمولة هو: {needed}")
                    return True

                # الخطوة الرابعة: تنفيذ العملية
                recipient_data = db.get(f"user_{target_id}")

                sender_data["coins"] -= total_required
                recipient_data["coins"] += amount

                db.set(f"user_{user_id}", sender_data)
                db.set(f"user_{target_id}", recipient_data)

                # إشعارات النجاح
                formatted_sent = get_formatted_currency(user_id, amount)
                await conv.send_message(f"✅ تم تحويل {formatted_sent} بنجاح إلى المستلم `{target_id}`.")

                # إشعار المستلم
                try:
                    await event.client.send_message(
                        target_id,
                        f"💰 **وصلتك حوالة جديدة!**\n\nالمبلغ: {formatted_sent}\nمن قبل: `{user_id}`"
                    )
                except:
                    pass

            except ValueError:
                await conv.send_message("❌ يرجى إدخال أرقام صحيحة فقط.")
            except asyncio.TimeoutError:
                await conv.send_message("⏳ انتهى وقت الجلسة، يرجى المحاولة مرة أخرى.")

        return True

    return False