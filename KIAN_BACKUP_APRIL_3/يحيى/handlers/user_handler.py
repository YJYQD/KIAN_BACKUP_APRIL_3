from telethon import Button
import asyncio


async def handle_user(event, data, user_id, **ctx):
    db = ctx["db"]
    lang = ctx["lang_manager"]
    # ملاحظة: storage_manager ممرر ولكن غير مستخدم هنا

    if data == "support":
        msg = lang.get_message(user_id, 'SUPPORT_MESSAGE')
        buttons = [[Button.url("👨‍💻 الدعم الفني", "https://t.me/mYJYQD")],
                   [Button.inline(lang.get_message(user_id, 'BACK_BUTTON'), data="main")]]
        await event.edit(msg, buttons=buttons)
        return True

    # --- تفعيل نظام إدخال كود الخصم (تم الإصلاح هنا) ---
    if data == "apply_coupon":
        discount_system = ctx["discount_system"]
        async with event.client.conversation(user_id, timeout=60) as conv:
            # يجب استخدام send_message بدلاً من edit لبدء المحادثة بشكل سليم
            await conv.send_message("🎟️ **يرجى إرسال كود الخصم الآن:**")

            try:
                code_msg = await conv.get_response()
                code = code_msg.text.strip().upper()

                valid, res = discount_system.is_code_valid(code, user_id)
                if valid:
                    user_data = db.get(f"user_{user_id}") or {}
                    user_data["active_coupon"] = code
                    db.set(f"user_{user_id}", user_data)
                    await code_msg.reply(
                        f"✅ تم تفعيل الكود بنجاح! ستحصل على خصم بقيمة {res['value']}% في عمليتك القادمة.")
                else:
                    await code_msg.reply(res)
            except asyncio.TimeoutError:
                await event.respond("⚠️ انتهى وقت إدخال الكود، يرجى المحاولة مرة أخرى.")
            except Exception as e:
                print(f"Error in coupon: {e}")
        return True

    if data == "liscgh":
        rules = db.get("rules_text") or lang.get_message(user_id, 'RULES_MESSAGE')
        await event.edit(f"📜 **قوانين واتفاقية الاستخدام:**\n\n{rules}",
                         buttons=[[Button.inline(lang.get_message(user_id, 'BACK_BUTTON'), data="main")]])
        return True

    return False