from pyrogram import Client
import asyncio
import os
from dotenv import load_dotenv

# تحميل البيانات من .env
load_dotenv()
api_id = int(os.getenv("API_ID", "0"))
api_hash = os.getenv("API_HASH", "")

async def main():
    # قمنا بتغيير ":memory:" إلى "temp_session" لحل مشكلة قاعدة البيانات
    app = Client("temp_session", api_id=api_id, api_hash=api_hash)
    async with app:
        session_str = await app.export_session_string()
        me = await app.get_me()
        print("\n" + "="*50)
        print(f"✅ تم استخراج الجلسة للرقم: {me.phone_number}")
        print("-" * 50)
        print(f"🔑 انسخ كود السشن التالي (يبدأ بـ BQ...):\n")
        print(session_str)
        print("="*50 + "\n")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"❌ حدث خطأ: {e}")