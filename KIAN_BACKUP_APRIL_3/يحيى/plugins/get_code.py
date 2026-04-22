import os

try:
    from pyrogram import Client
    import asyncio, re, json
    from kvsqlite.sync import Client as uu
    import time, datetime
    from datetime import timedelta
except:
    os.system("pip install pyrogram")
    try:
        from pyrogram import Client
        import asyncio, re, json
        from kvsqlite.sync import Client as uu
        import time, datetime
        from datetime import timedelta
    except Exception as errors:
        print('An Erorr with: ' + str(errors))
        exit(0)

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")

async def get_code(session):
    try:
        app = Client(":memory:", session_string=session, api_id=API_ID, api_hash=API_HASH, in_memory=True)
        await app.start()

        async for message in app.get_chat_history(777000, limit=1):
            code_match = re.search(r'\b(\d{5})\b', message.text)
            if code_match:
                code = code_match.group(1)
                if code.isdigit():
                    await app.stop()
                    return code

        await app.stop()
        return None
    except Exception as a:
        return None

async def change_password(session, old_password, new_password):
    c = Client('::memory::', in_memory=True, api_hash='2d0390f5ccf197be30a21a15d6d7e529', api_id=29157277, lang_code="ar", no_updates=True, session_string=session)
    try:
        await c.start()
    except:
        return False
    try:
        await c.change_cloud_password(old_password, new_password)
        await c.stop()
        return True
    except:
        return False

async def enable_password(session, new_password):
    c = Client('::memory::', in_memory=True, api_hash='2d0390f5ccf197be30a21a15d6d7e529', api_id=29157277, lang_code="ar", no_updates=True, session_string=session)
    try:
        await c.start()
    except:
        return False
    try:
        await c.enable_cloud_password(new_password)
        await c.stop()
        return True
    except:
        return False