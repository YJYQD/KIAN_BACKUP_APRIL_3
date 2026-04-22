# -*- coding: utf-8 -*-
import time, random, string
from datetime import datetime


class DiscountSystem:
    def __init__(self, db):
        self.db = db
        self.init_discounts()

    def init_discounts(self):
        """تهيئة جداول الخصومات في قاعدة البيانات"""
        if not self.db.exists("discount_codes"):
            self.db.set("discount_codes", {})
        if not self.db.exists("user_discounts"):
            self.db.set("user_discounts", {})

    def create_discount_code(self, discount_type="percentage", value=10, max_uses=None, expiry_days=30, description=""):
        """توليد كود خصم فريد وحفظه"""
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        codes = self.db.get("discount_codes") or {}
        expiry_time = time.time() + (expiry_days * 24 * 60 * 60)

        codes[code] = {
            "type": discount_type,
            "value": float(value),
            "max_uses": max_uses,
            "current_uses": 0,
            "used_by": [],
            "expires_at": expiry_time,
            "description": description,
            "is_active": True
        }
        self.db.set("discount_codes", codes)
        return code

    def is_code_valid(self, code, user_id):
        """التحقق الشامل من صلاحية الكود للمستخدم"""
        codes = self.db.get("discount_codes") or {}
        discount = codes.get(code.upper())

        if not discount: return False, "❌ الكود غير موجود"
        if not discount.get("is_active"): return False, "❌ الكود معطل حالياً"
        if time.time() > discount["expires_at"]: return False, "❌ الكود منتهي الصلاحية"
        if discount["max_uses"] and discount["current_uses"] >= discount["max_uses"]:
            return False, "❌ انتهى عدد الاستخدامات المسموح به لهذا الكود"
        if user_id in discount.get("used_by", []): return False, "❌ لقد استخدمت هذا الكود مسبقاً"

        return True, discount

    def apply_discount(self, code, original_price, user_id):
        """تطبيق الخصم وحساب السعر النهائي"""
        valid, result = self.is_code_valid(code, user_id)
        if not valid: return original_price, 0, result

        discount = result
        if discount["type"] == "percentage":
            amt = original_price * (discount["value"] / 100)
        else:
            amt = min(discount["value"], original_price)

        final_price = max(0.1, original_price - amt)

        # تحديث بيانات الكود في القاعدة
        codes = self.db.get("discount_codes")
        codes[code.upper()]["current_uses"] += 1
        codes[code.upper()]["used_by"].append(user_id)
        self.db.set("discount_codes", codes)

        return final_price, amt, f"✅ تم تطبيق خصم بقيمة {amt:.2f} ﷼"


def setup_discount_system(db):
    return DiscountSystem(db)