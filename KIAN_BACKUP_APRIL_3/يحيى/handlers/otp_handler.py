# -*- coding: utf-8 -*-
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import (
    PhoneCodeInvalidError,
    PhoneCodeExpiredError,
    SessionPasswordNeededError,
    FloodWaitError
)
import asyncio

# تخزين العملاء والبيانات مؤقتاً
otp_clients = {}
otp_data = {}


async def cleanup_otp(user_id):
    """تنظيف الجلسة وإغلاق الاتصال بعد 5 دقائق"""
    await asyncio.sleep(300)
    if user_id in otp_clients:
        client = otp_clients.pop(user_id, None)
        if client:
            try:
                await client.disconnect()
            except:
                pass
    otp_data.pop(user_id, None)


async def send_otp(user_id, phone, api_id, api_hash):
    """إرسال كود التحقق"""
    if user_id in otp_clients:
        # إذا كان هناك طلب نشط، نغلقه أولاً لبدء طلب جديد
        old_client = otp_clients.pop(user_id)
        await old_client.disconnect()

    try:
        client = TelegramClient(StringSession(), api_id, api_hash)
        await client.connect()

        # طلب إرسال الكود
        result = await client.send_code_request(phone)

        otp_clients[user_id] = client
        otp_data[user_id] = {
            "phone": phone,
            "hash": result.phone_code_hash
        }

        # بدء مهمة التنظيف التلقائي
        asyncio.create_task(cleanup_otp(user_id))
        return True
    except FloodWaitError as e:
        print(f"⚠️ انتظر {e.seconds} ثانية بسبب قيود تيليجرام")
        return False
    except Exception as e:
        print(f"❌ خطأ في إرسال الكود: {e}")
        return False


async def verify_otp(user_id, code):
    """التحقق من الكود وحفظ الجلسة"""
    client = otp_clients.get(user_id)
    data = otp_data.get(user_id)

    if not client or not data:
        return "no_session"

    try:
        # محاولة تسجيل الدخول
        await client.sign_in(
            phone=data["phone"],
            code=code,
            phone_code_hash=data["hash"]
        )

        # إذا نجح التسجيل، نحفظ الجلسة ونغلق الاتصال
        session = client.session.save()
        phone = data["phone"]

        await client.disconnect()
        otp_clients.pop(user_id, None)
        otp_data.pop(user_id, None)

        return {
            "status": True,
            "session": session,
            "phone": phone
        }

    except PhoneCodeInvalidError:
        return "invalid_code"
    except PhoneCodeExpiredError:
        return "expired_code"
    except SessionPasswordNeededError:
        return "2fa_required"
    except Exception as e:
        print(f"❌ خطأ غير معروف في التحقق: {e}")
        return "error"