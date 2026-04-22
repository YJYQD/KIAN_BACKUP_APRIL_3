import time
import random


class StorageManager:
    def __init__(self, db):
        self.db = db
        self.init_storage()

    def init_storage(self):
        """تجهيز صناديق التخزين لكل نوع"""
        sections = ["normal", "fake", "fraud", "old_creation"]
        for section in sections:
            key = f"storage_{section}"
            if not self.db.exists(key):
                self.db.set(key, [])

        # تهيئة إعدادات البيع التلقائي إذا لم توجد
        if not self.db.exists("auto_sell_config"):
            self.db.set("auto_sell_config", {"enabled": False})

    def get_storage_stats(self):
        """جلب إحصائيات التخزين بدقة من كافة الصناديق"""
        stats = {"total": 0, "stored": 0, "selling": 0, "sold": 0}
        sections = ["normal", "fake", "fraud", "old_creation"]

        for section in sections:
            all_nums = self.db.get(f"storage_{section}") or []
            stats["total"] += len(all_nums)
            stats["stored"] += len([x for x in all_nums if x.get("status") == "stored"])
            stats["selling"] += len([x for x in all_nums if x.get("status") == "selling"])
            stats["sold"] += len([x for x in all_nums if x.get("status") == "sold"])
        return stats

    def add_account(self, account_type, account_data):
        """إضافة حساب لصندوق معين"""
        db_key = f"storage_{account_type}"
        data = self.db.get(db_key) or []

        account_data["added_time"] = time.time()
        account_data["status"] = "stored"

        data.append(account_data)
        self.db.set(db_key, data)
        return True

    def get_sold_numbers(self):
        """جلب كافة الأرقام المتاحة للإدارة (تستخدم في لوحة الأدمن)"""
        all_numbers = []
        sections = ["normal", "fake", "fraud", "old_creation"]
        for section in sections:
            nums = self.db.get(f"storage_{section}") or []
            all_numbers.extend(nums)
        return all_numbers

    def get_number_by_phone(self, phone):
        """البحث عن رقم محدد في كافة الأقسام"""
        all_nums = self.get_sold_numbers()
        for num in all_nums:
            if str(num.get("phone_number")) == str(phone):
                return num
        return None

    def remove_number(self, phone_number):
        """حذف رقم نهائياً من أي قسم وجد فيه"""
        sections = ["normal", "fake", "fraud", "old_creation"]
        for section in sections:
            key = f"storage_{section}"
            nums = self.db.get(key) or []
            new_nums = [n for n in nums if str(n.get("phone_number")) != str(phone_number)]
            if len(nums) != len(new_nums):
                self.db.set(key, new_nums)
                return True
        return False

    def update_number_status(self, phone_number, status):
        """تحديث حالة الرقم (Selling, Stored, Sold)"""
        sections = ["normal", "fake", "fraud", "old_creation"]
        for section in sections:
            key = f"storage_{section}"
            nums = self.db.get(key) or []
            for n in nums:
                if str(n.get("phone_number")) == str(phone_number):
                    n["status"] = status
                    self.db.set(key, nums)
                    return True
        return False

    def get_random_number(self, account_type, country):
        """سحب رقم عشوائي جاهز للبيع"""
        db_key = f"storage_{account_type}"
        accounts = self.db.get(db_key) or []
        valid = [acc for acc in accounts if acc.get("country") == country and acc.get("status") == "stored"]
        return random.choice(valid) if valid else None

    # --- إعدادات البيع التلقائي ---
    def get_auto_sell_status(self):
        return self.db.get("auto_sell_config") or {"enabled": False}

    def set_auto_sell(self, status: bool):
        self.db.set("auto_sell_config", {"enabled": status})

    def get_code(self, phone_number):
        """دالة افتراضية لجلب الكود (يتم تحديثها عند وصول الرسالة)"""
        num = self.get_number_by_phone(phone_number)
        return num.get("last_code") if num else None

    def get_available_numbers(self, account_type="normal"):
        """جلب الأرقام المتاحة فقط للبيع حسب النوع"""
        db_key = f"storage_{account_type}"
        all_nums = self.db.get(db_key) or []
        return [n for n in all_nums if n.get("status") == "stored"]