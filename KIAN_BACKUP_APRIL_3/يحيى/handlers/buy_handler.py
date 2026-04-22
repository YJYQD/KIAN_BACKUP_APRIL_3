# -*- coding: utf-8 -*-
from telethon import Button
import random
import asyncio
import os

# تأكد من أن المسار صحيح حسب مجلداتك
try:
    from handlers.otp_handler import send_otp, verify_otp
except ImportError:
    from otp_handler import send_otp, verify_otp

buy_states = {}

# =========================
# بداية الشراء
# =========================
async def start_buy(event, user_id, account_type, country, price):
    buy_states[user_id] = {
        "account_type": account_type,
        "country": country,
        "price": price,
        "status": "confirm"
    }

    await event.edit(
        f"📦 **تأكيد الشراء**\n\n"
        f"📂 القسم: {account_type}\n"
        f"🌍 الدولة: {country}\n"
        f"💰 السعر: {price} SAR\n\n"
        f"هل تريد المتابعة؟",
        buttons=[
            [Button.inline("✅ تأكيد الشراء", data="confirm_buy")],
            [Button.inline("❌ إلغاء", data="cancel_buy")]
        ]
    )

# =========================
# تأكيد الشراء (سحب الرقم)
# =========================
async def confirm_buy(event, user_id, storage_manager, db):
    if user_id not in buy_states:
        await event.answer("⚠️ انتهت الجلسة، ابدأ من جديد", alert=True)
        return

    state = buy_states[user_id]

    # 1. التحقق من الرصيد
    user_data = db.get(f"user_{user_id}") or {"coins": 0}
    if user_data.get("coins", 0) < state["price"]:
        await event.answer("❌ رصيدك غير كافي لإتمام هذه العملية", alert=True)
        return

    # 2. سحب رقم متاح بناءً على القسم والدولة
    available = storage_manager.get_available_numbers(state["account_type"])
    numbers_in_country = [n for n in available if n.get('country') == state['country']]

    if not numbers_in_country:
        await event.edit("❌ نعتذر، انتهت الأرقام المتاحة لهذه الدولة حالياً.")
        buy_states.pop(user_id, None)
        return

    number = random.choice(numbers_in_country)
    buy_states[user_id]["number_data"] = number
    buy_states[user_id]["status"] = "waiting_code"

    await event.edit(
        f"📱 **الرقم المحجوز لك:**\n\n"
        f"`+{number['phone_number']}`\n\n"
        f"قم بطلب الكود في تطبيق تيليجرام ثم اضغط الزر بالأسفل 👇",
        buttons=[
            [Button.inline("📩 طلب الكود الآن", data="request_code")],
            [Button.inline("❌ إلغاء العملية", data="cancel_buy")]
        ]
    )

# =========================
# طلب الكود (إرسال OTP)
# =========================
async def request_code(event, user_id):
    state = buy_states.get(user_id)
    if not state or "number_data" not in state:
        await event.answer("❌ خطأ: لا يوجد رقم محجوز", alert=True)
        return

    phone = state["number_data"]["phone_number"]
    await event.answer("⏳ جاري طلب الكود من سيرفرات تيليجرام...", alert=False)

    ok = await send_otp(user_id, phone)
    if ok:
        await event.answer("✅ تم إرسال الكود بنجاح، يرجى كتابته هنا في الشات 👇", alert=True)
    else:
        await event.answer("❌ فشل إرسال الكود، قد يكون الرقم محظوراً أو استهلك المحاولات.", alert=True)

# =========================
# استقبال الكود (من الرسائل)
# =========================
async def handle_otp_input(event, user_id, text, storage_manager, verify_otp_func=None):
    if user_id not in buy_states:
        return False

    state = buy_states[user_id]
    if state["status"] != "waiting_code":
        return False

    v_func = verify_otp_func if verify_otp_func else verify_otp
    result = await v_func(user_id, text)

    if result == True:
        buy_states[user_id]["status"] = "activated"
        await event.reply(
            "✅ **تم التحقق بنجاح وتفعيل الرقم!**\n\nيرجى الضغط على تأكيد الاستلام لإتمام العملية وخصم المبلغ وتسليمك الحساب.",
            buttons=[[Button.inline("✅ تأكيد الاستلام والتشغيل", data="confirm_login")]]
        )
    elif result == "invalid_code":
        await event.reply("❌ الكود الذي أدخلته غير صحيح، حاول مجدداً:")
    elif result == "expired_code":
        await event.reply("⌛ انتهت صلاحية الكود، اطلب كود جديد.")
    elif result == "2fa_required":
        await event.reply("🔐 هذا الحساب محمي بالتحقق بخطوتين، تم تجربة كلمة السر الافتراضية وفشلت. يرجى التواصل مع الدعم.")
    else:
        await event.reply("❌ حدث خطأ غير متوقع أثناء التحقق.")

    return True

# =========================
# تأكيد الاستلام النهائي (تسليم المنتج)
# =========================
async def confirm_login(event, user_id, storage_manager, db):
    if user_id not in buy_states:
        return

    state = buy_states[user_id]
    if state["status"] != "activated":
        await event.answer("⚠️ لم يتم تفعيل الرقم بعد", alert=True)
        return

    number = state["number_data"]

    # 1. خصم الرصيد فعلياً
    user_data = db.get(f"user_{user_id}")
    user_data["coins"] -= state["price"]
    db.set(f"user_{user_id}", user_data)

    # 2. تسليم المنتج للمستخدم (إرسال الجلسة)
    try:
        if "session_path" in number and number["session_path"]:
            # تسليم ملف الجلسة للأدمن أو المشتري
            await event.client.send_file(
                user_id,
                number["session_path"],
                caption=f"✅ **تم شراء الحساب بنجاح!**\n\n📱 الرقم: `+{number['phone_number']}`\n🌍 الدولة: {state['country']}\n📂 القسم: {state['account_type']}"
            )
        elif "session" in number:
            # تسليم كود String Session
            await event.client.send_message(
                user_id,
                f"✅ **تم شراء الحساب بنجاح!**\n\n📱 الرقم: `+{number['phone_number']}`\n🔑 كود الجلسة (String):\n`{number['session']}`"
            )
    except Exception as e:
        await event.respond(f"⚠️ تمت العملية ولكن فشل إرسال الملف، يرجى تصوير هذه الرسالة للدعم: {e}")

    # 3. تحديث حالة الرقم في المخزن ليصبح "مباع"
    storage_manager.update_number_status(number["phone_number"], "sold")

    await event.edit(
        f"🎉 **مبروك! تمت العملية بنجاح**\n\n"
        f"💰 المبلغ المخصوم: {state['price']} SAR\n\n"
        f"نتمنى لك تجربة سعيدة مع كيان سيم!"
    )

    # 4. إرسال إشعار لقناة التفعيلات
    try:
        await event.client.send_message(
            "QQQ_5i",
            f"✅ **عملية شراء ناجحة**\n\n"
            f"👤 المشتري: `{user_id}`\n"
            f"🌍 الدولة: {state['country']}\n"
            f"📂 القسم: {state['account_type']}\n"
            f"💰 السعر: {state['price']} SAR"
        )
    except:
        pass

    buy_states.pop(user_id, None)

# =========================
# إلغاء الشراء
# =========================
async def cancel_buy(event, user_id):
    buy_states.pop(user_id, None)
    await event.edit("❌ تم إلغاء عملية الشراء وإخلاء الرقم.")