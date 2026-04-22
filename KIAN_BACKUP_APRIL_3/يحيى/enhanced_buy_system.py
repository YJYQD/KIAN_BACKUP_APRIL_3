import asyncio
import random
import os
from telethon import Button, events
from pyrogram import Client

COUNTRY_FLAGS = {
    'مصر': '🇪🇬', 'السعودية': '🇸🇦', 'الامارات': '🇦🇪', 'الكويت': '🇰🇼',
    'البحرين': '🇧🇭', 'قطر': '🇶🇦', 'عمان': '🇴🇲', 'الاردن': '🇯🇴',
    'العراق': '🇮🇶', 'اليمن': '🇾🇪', 'المغرب': '🇲🇦', 'الجزائر': '🇩🇿',
    'تونس': '🇹🇳', 'ليبيا': '🇱🇾', 'السودان': '🇸🇩', 'تركيا': '🇹🇷',
    'روسيا': '🇷🇺', 'امريكا': '🇺🇸', 'الصين': '🇨🇳', 'فلسطين': '🇵🇸'
}


class EnhancedBuySystem:
    def __init__(self, client, db, lang_manager, storage_manager, discount_system, db_sections, ACCOUNT_TYPE_META):
        self.client = client
        self.db = db
        self.lang_manager = lang_manager
        self.storage_manager = storage_manager
        self.discount_system = discount_system
        self.db_sections = db_sections
        self.ACCOUNT_TYPE_META = ACCOUNT_TYPE_META
        self.active_purchases = {}

    def get_current_section_info(self, user_id):
        pk = f"purchase_{user_id}"
        category = self.active_purchases.get(pk, {}).get('category', 'normal')
        return category, self.db_sections.get(category, self.db)

    def get_section_countries(self, user_id):
        category, section_db = self.get_current_section_info(user_id)
        if category == "normal":
            return section_db.get("countries") or []
        else:
            meta = self.ACCOUNT_TYPE_META.get(category, {})
            countries_dict = section_db.get(meta.get("countries_key")) or {}
            return [{"name": n, "calling_code": d.get("calling_code"), "price": d.get("price")} for n, d in
                    countries_dict.items()]

    def format_price(self, user_id, price_sar):
        user_data = self.db.get(f"user_{user_id}") or {}
        currency = user_data.get("currency", "SAR")
        rates = self.db.get("currency_rates") or {"SAR": 1.0, "YER": 66.67, "USD": 0.267}
        if currency == "YER": return f"{float(price_sar) * rates.get('YER', 66.67):,.0f} ﷼ يمني"
        if currency == "USD": return f"{float(price_sar) * rates.get('USD', 0.267):.2f} $"
        return f"{price_sar:.2f} ﷼ سعودي"

    # 🛠️ الدالة المعدلة لدعم الصفحات والتنسيق الخاص بقسم الإنشاء
    async def show_countries_menu(self, event, user_id, page=0):
        category, section_db = self.get_current_section_info(user_id)
        countries = self.get_section_countries(user_id)

        if not countries:
            await event.edit("❌ لا توجد دول متاحة في هذا القسم حالياً",
                             buttons=[[Button.inline("⦉ رجوع ⦊", data="main")]])
            return

        buttons = [[Button.inline("🔍 بحث عن دولة", data="enhanced_search_country")]]

        # 💎 منطق خاص لـ "قسم الإنشاء" فقط: 4 أزرار تحت بعض مع صفحات
        if category == "old_creation":
            per_page = 4
            start = page * per_page
            end = start + per_page
            current_page_countries = countries[start:end]

            for c in current_page_countries:
                flag = COUNTRY_FLAGS.get(c['name'], '🌍')
                # إضافة كل دولة في صف مستقل (تحت بعض)
                buttons.append([Button.inline(f"{flag} {c['name']} | self.format_price(user_id, c['price'])",
                                              data=f"enhanced_country_{c['calling_code']}")])

            # أزرار التنقل بين الصفحات
            nav_buttons = []
            if page > 0:
                nav_buttons.append(Button.inline("⬅️ السابق", data=f"enhanced_page_{page - 1}"))
            if end < len(countries):
                nav_buttons.append(Button.inline("التالي ➡️", data=f"enhanced_page_{page + 1}"))

            if nav_buttons:
                buttons.append(nav_buttons)

        # 🏠 بقية الأقسام: نظام الزرين بجانب بعض كالمعتاد
        else:
            row = []
            for c in countries:
                flag = COUNTRY_FLAGS.get(c['name'], '🌍')
                btn = Button.inline(f"{flag} {c['name']} | {c['price']:.0f} SAR",
                                    data=f"enhanced_country_{c['calling_code']}")
                if len(row) < 2:
                    row.append(btn)
                else:
                    buttons.append(row);
                    row = [btn]
            if row: buttons.append(row)

        buttons.append([Button.inline("🔙 رجوع", data="main")])

        msg_text = self.lang_manager.get_message(user_id, 'COUNTRY_LIST')
        # إضافة مؤشر الصفحة في قسم الإنشاء
        if category == "old_creation":
            msg_text += f"\n\n📄 الصفحة الحالية: {page + 1}"

        await event.edit(msg_text, buttons=buttons)

    async def search_country(self, event, user_id):
        async with self.client.conversation(user_id, timeout=60) as conv:
            await conv.send_message("**🔍 أرسل اسم الدولة أو رمزها (مثال: مصر أو 20):**")
            try:
                res = await conv.get_response()
                query = res.text.strip().lower()
                countries = self.get_section_countries(user_id)
                found = [c for c in countries if query in c['name'].lower() or query in str(c['calling_code'])]
                if found:
                    buttons = []
                    for c in found: buttons.append([Button.inline(f"🌐 {c['name']} (+{c['calling_code']})",
                                                                  data=f"enhanced_country_{c['calling_code']}")])
                    buttons.append([Button.inline("🔙 رجوع", data="enhanced_buy")])
                    await conv.send_message(f"✅ تم العثور على {len(found)} دولة:", buttons=buttons)
                else:
                    await conv.send_message("❌ لم يتم العثور على نتائج.",
                                            buttons=[[Button.inline("🔙 رجوع", data="enhanced_buy")]])
            except:
                pass

    async def show_country_numbers(self, event, user_id, calling_code):
        category, section_db = self.get_current_section_info(user_id)
        countries = self.get_section_countries(user_id)
        country = next((c for c in countries if str(c['calling_code']) == str(calling_code)), None)
        if not country: return
        if category == "normal":
            accounts = section_db.get(f"accounts_{calling_code}") or []
        else:
            accounts = (section_db.get(self.ACCOUNT_TYPE_META[category]["db_key"]) or {}).get(country['name']) or []
        if not accounts:
            await event.answer("❌ لا توجد أرقام متاحة حالياً", alert=True);
            return
        await self.show_number_confirmation(event, user_id, calling_code, random.randint(0, len(accounts) - 1))

    async def show_number_confirmation(self, event, user_id, calling_code, account_index):
        category, section_db = self.get_current_section_info(user_id)
        countries = self.get_section_countries(user_id)
        country = next((c for c in countries if str(c['calling_code']) == str(calling_code)), None)
        if not country: return
        if category == "normal":
            accounts = section_db.get(f"accounts_{calling_code}") or []
        else:
            accounts = (section_db.get(self.ACCOUNT_TYPE_META[category]["db_key"]) or {}).get(country['name']) or []
        account = accounts[account_index]

        pk = f"purchase_{user_id}"
        if pk not in self.active_purchases: self.active_purchases[pk] = {}

        self.active_purchases[pk].update({
            'calling_code': calling_code, 'account_index': int(account_index),
            'phone_number': str(account['phone_number']),
            'country_name': str(country['name']), 'price': float(country['price']),
            'session': str(account.get('session') or account.get('session_path')),
            'two_step': str(account.get('two_step', 'لا يوجد')),
            'applied_code': None
        })
        msg = f"**✅ تأكيد الشراء**\n\n🌎 الدولة: {country['name']}\n💰 السعر: {self.format_price(user_id, self.active_purchases[pk]['price'])}\n\n**سيتم عرض الرقم بعد التأكيد.**"
        buttons = [[Button.inline("💱 تغيير العملة", data=f"enhanced_currency_{calling_code}_{account_index}")],
                   [Button.inline("🎁 كود خصم", data=f"enhanced_discount_{calling_code}_{account_index}")],
                   [Button.inline("تأكيد الشراء ✅", data=f"enhanced_confirm_{user_id}")],
                   [Button.inline("إلغاء ❌", data="enhanced_buy")]]
        await event.edit(msg, buttons=buttons)

    async def apply_discount(self, event, user_id, calling_code, account_index):
        async with self.client.conversation(user_id, timeout=60) as conv:
            await conv.send_message("**🎟️ أرسل كود الخصم الآن:**")
            try:
                res = await conv.get_response()
                code = res.text.strip()
                pk = f"purchase_{user_id}"

                coupons = self.db.get("discount_codes") or {}
                if code not in coupons:
                    await conv.send_message("❌ كود الخصم هذا غير موجود.")
                    return

                c_data = coupons[code]
                if c_data.get('current_uses', 0) >= c_data.get('max_uses', 0):
                    await conv.send_message("⚠️ عذراً، هذا الكود وصل للحد الأقصى من الاستخدام.")
                    return

                discount_percent = c_data.get('percent', 0)
                original_price = self.active_purchases[pk]['price']
                discount_amount = original_price * (discount_percent / 100)
                final_price = original_price - discount_amount

                self.active_purchases[pk]['price'] = final_price
                self.active_purchases[pk]['applied_code'] = code

                await conv.send_message(f"✅ تم تطبيق خصم {discount_percent}% بنجاح!")
                await self.show_number_confirmation(event, user_id, calling_code, account_index)
            except Exception as e:
                print(f"Error in apply_discount: {e}")
                await conv.send_message("❌ حدث خطأ أثناء تطبيق الكود.")

    async def process_purchase(self, event, user_id):
        pk = f"purchase_{user_id}"
        if pk not in self.active_purchases: return
        info = self.active_purchases[pk]
        category, section_db = self.get_current_section_info(user_id)
        user_data = self.db.get(f"user_{user_id}")

        if user_data['coins'] < info['price']:
            await event.answer("❌ رصيدك غير كافي لشراء هذا الرقم", alert=True)
            return

        try:
            if category == "normal":
                accs = section_db.get(f"accounts_{info['calling_code']}")
                lock = asyncio.Lock()

                async with lock:
                    accs.pop(info['account_index'])
                section_db.set(f"accounts_{info['calling_code']}", accs)
            else:
                meta = self.ACCOUNT_TYPE_META[category]
                all_accs = section_db.get(meta["db_key"])
                all_accs[info['country_name']].pop(info['account_index'])
                section_db.set(meta["db_key"], all_accs)
        except:
            await event.answer("❌ عذراً، الرقم لم يعد متاحاً.", alert=True)
            return

        user_data['coins'] -= info['price']
        self.db.set(f"user_{user_id}", user_data)

        applied_code = info.get('applied_code')
        if applied_code:
            coupons = self.db.get("discount_codes") or {}
            if applied_code in coupons:
                coupons[applied_code]['current_uses'] += 1
                self.db.set("discount_codes", coupons)

        self.active_purchases[f"code_{user_id}"] = info
        await event.edit(
            f"**🎉 تم الشراء بنجاح!**\n\nالرقم: `+{info['phone_number']}`\nالسعر: {self.format_price(user_id, info['price'])}",
            buttons=[[Button.inline("📩 طلب كود التحقق", data=f"enhanced_request_code_{user_id}")]])

    async def request_code_manual(self, event, user_id):
        info = self.active_purchases.get(f"code_{user_id}")
        if not info: return
        await event.edit("🔄 جاري طلب الكود...")
        try:
            from plugins.get_code import get_code
            code = await get_code(info['session'])
            if code:
                await self.send_purchase_notification(user_id, info['phone_number'], info['country_name'],
                                                      info['price'], info['two_step'], code)
                await event.edit(f"✅ الكود: `{code}`\n🔐 التحقق: `{info['two_step']}`",
                                 buttons=[[Button.inline("🚪 تسجيل خروج", data=f"enhanced_logout_{user_id}")]])
            else:
                await event.edit("❌ لم يصل الكود بعد، تأكد من طلب الكود في تطبيق التليجرام أولاً.",
                                 buttons=[[Button.inline("🔄 إعادة طلب", data=f"enhanced_request_code_{user_id}")]])
        except:
            await event.edit("❌ خطأ في الاتصال بالسيرفر.")

    async def logout_session(self, event, user_id):
        info = self.active_purchases.get(f"code_{user_id}")
        if not info: return
        await event.edit("🚪 جاري تسجيل الخروج لضمان أمان الحساب...")
        try:
            app = Client("logout_tmp", session_string=info['session'], api_id=int(os.getenv("API_ID")),
                         api_hash=os.getenv("API_HASH"), in_memory=True)
            async with app:
                await app.log_out()
        except:
            pass
        self.active_purchases.pop(f"code_{user_id}", None)
        await event.edit("✅ تم تسجيل الخروج بنجاح. شكراً لثقتك بنا!",
                         buttons=[[Button.inline("⦉ الرئيسية ⦊", data="main")]])

    async def send_purchase_notification(self, user_id, phone, country, price, two_step, code):
        trust_channel = self.db.get("trust_channel")
        if trust_channel:
            hidden_phone = f"+{phone[:-4]}****"
            msg = f"🛒 **عملية شراء ناجحة!**\n\n🏳️ الدولة: {country}\n☎️ الرقم: `{hidden_phone}`\n💰 السعر: {price} SAR\n📥 الكود المستلم: `{code}`\n\n✅ تـم الـتـسـلـيـم بـنـجـاح."
            try:
                await self.client.send_message(trust_channel, msg)
            except:
                pass

    # 🎮 تعديل معالج الكولباك لاستقبال بيانات الصفحات
    async def handle_callback(self, event, data, user_id):
        if data == "enhanced_buy": await self.show_countries_menu(event, user_id); return True

        # التقاط أمر تغيير الصفحة
        if data.startswith("enhanced_page_"):
            page_num = int(data.split("_")[2])
            await self.show_countries_menu(event, user_id, page=page_num);
            return True

        if data == "enhanced_search_country": await self.search_country(event, user_id); return True
        if data.startswith("enhanced_country_"): await self.show_country_numbers(event, user_id,
                                                                                 data.replace("enhanced_country_",
                                                                                              "")); return True
        if data.startswith("enhanced_confirm_"): await self.process_purchase(event, user_id); return True
        if data.startswith("enhanced_request_code_"): await self.request_code_manual(event, user_id); return True
        if data.startswith("enhanced_logout_"): await self.logout_session(event, user_id); return True
        if data.startswith("enhanced_discount_"):
            parts = data.split("_");
            await self.apply_discount(event, user_id, parts[2], parts[3]);
            return True
        if data.startswith("enhanced_currency_"):
            u_data = self.db.get(f"user_{user_id}");
            curr = "USD" if u_data.get("currency") == "SAR" else "SAR"
            u_data["currency"] = curr;
            self.db.set(f"user_{user_id}", u_data)
            parts = data.split("_");
            await self.show_number_confirmation(event, user_id, parts[2], parts[3]);
            return True
        return False


def setup_enhanced_buy_system(client, db, lang_manager, storage_manager, discount_system, db_sections,
                              ACCOUNT_TYPE_META):
    enhanced_system = EnhancedBuySystem(client, db, lang_manager, storage_manager, discount_system, db_sections,
                                        ACCOUNT_TYPE_META)


