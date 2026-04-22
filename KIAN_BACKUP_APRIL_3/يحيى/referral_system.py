# referral_system.py
import random
import string
from telethon import Button

class ReferralSystem:
    def __init__(self, db):
        self.db = db
        
        # تهيئة الجداول إذا لم تكن موجودة
        if not db.exists("referral_settings"):
            db.set("referral_settings", {"reward": 0.01})
            
        if not db.exists("referral_links"):
            db.set("referral_links", {})
            
        if not db.exists("referral_users"):
            db.set("referral_users", {})
            
        if not db.exists("referral_stats"):
            db.set("referral_stats", {})
            
        if not db.exists("pending_referrals"):
            db.set("pending_referrals", {})

    def generate_referral_code(self, user_id):
        """إنشاء كود دعوة فريد للمستخدم"""
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        links = self.db.get("referral_links")
        
        # التأكد من أن الكود فريد
        while code in links:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            
        links[code] = user_id
        self.db.set("referral_links", links)
        return code

    def get_referral_code(self, user_id):
        """الحصول على كود الدعوة للمستخدم (ينشئ واحداً إذا لم يكن موجوداً)"""
        links = self.db.get("referral_links")
        
        # البحث عن كود موجود للمستخدم
        for code, uid in links.items():
            if uid == user_id:
                return code
                
        # إنشاء كود جديد إذا لم يكن موجوداً
        return self.generate_referral_code(user_id)

    def get_user_by_referral_code(self, code):
        """الحصول على معرف المستخدم من كود الدعوة"""
        links = self.db.get("referral_links")
        return links.get(code)

    def add_referred_user(self, referrer_id, referred_id):
        """إضافة مستخدم تمت دعوته"""
        users = self.db.get("referral_users")
        
        if referrer_id not in users:
            users[referrer_id] = []
            
        if referred_id not in users[referrer_id]:
            users[referrer_id].append(referred_id)
            self.db.set("referral_users", users)
            return True
            
        return False

    def get_referred_users(self, user_id):
        """الحصول على قائمة المستخدمين الذين تمت دعوتهم"""
        users = self.db.get("referral_users")
        return users.get(user_id, [])

    def get_referral_reward(self):
        """الحصول على مكافأة الدعوة الحالية"""
        settings = self.db.get("referral_settings")
        return settings.get("reward", 0.01)

    def set_referral_reward(self, reward):
        """تعيين مكافأة دعوة جديدة"""
        settings = self.db.get("referral_settings")
        settings["reward"] = reward
        self.db.set("referral_settings", settings)

    def get_referral_stats(self, user_id):
        """الحصول على إحصائيات الدعوة للمستخدم"""
        stats = self.db.get("referral_stats")
        user_stats = stats.get(str(user_id), {"total_referred": 0, "total_earned": 0.0})
        user_stats["total_referred"] = len(self.get_referred_users(user_id))
        return user_stats

    def update_referral_stats(self, user_id, earned):
        """تحديث إحصائيات الدعوة"""
        stats = self.db.get("referral_stats")
        
        if str(user_id) not in stats:
            stats[str(user_id)] = {"total_referred": 0, "total_earned": 0.0}
            
        stats[str(user_id)]["total_referred"] = len(self.get_referred_users(user_id))
        stats[str(user_id)]["total_earned"] += earned
        
        self.db.set("referral_stats", stats)

    def process_referral(self, referrer_id, referred_id):
        """معالجة الدعوة: إضافة الرصيد للمستخدم الذي دعا"""
        # تجنب إضافة الرصيد إذا كان المستخدم قد دخل بالفعل عبر رابط دعوة آخر
        if self.db.exists(f"user_{referred_id}"):
            return 0

        # إضافة المستخدم إلى قائمة المدعوين
        if self.add_referred_user(referrer_id, referred_id):
            # منح المكافأة للمستخدم الذي دعا
            reward = self.get_referral_reward()
            
            if self.db.exists(f"user_{referrer_id}"):
                user_data = self.db.get(f"user_{referrer_id}")
                user_data["coins"] += reward
                self.db.set(f"user_{referrer_id}", user_data)
                
                # تحديث الإحصائيات
                self.update_referral_stats(referrer_id, reward)
                
            return reward
            
        return 0

    def add_pending_referral(self, referrer_id, referred_id):
        """إضافة دعوة معلقة حتى اكتمال الاشتراك الإجباري"""
        if not self.db.exists("pending_referrals"):
            self.db.set("pending_referrals", {})
        
        pending_referrals = self.db.get("pending_referrals")
        pending_referrals[str(referred_id)] = referrer_id
        self.db.set("pending_referrals", pending_referrals)
        return True

    def get_pending_referral(self, referred_id):
        """الحصول على الدعوة المعلقة"""
        if not self.db.exists("pending_referrals"):
            return None
        
        pending_referrals = self.db.get("pending_referrals")
        return pending_referrals.get(str(referred_id))

    def complete_pending_referral(self, referred_id):
        """إكمال الدعوة المعلقة بعد الاشتراك الإجباري"""
        if not self.db.exists("pending_referrals"):
            return 0
        
        pending_referrals = self.db.get("pending_referrals")
        referrer_id = pending_referrals.get(str(referred_id))
        
        if not referrer_id:
            return 0
        
        # إزالة من القائمة المعلقة
        del pending_referrals[str(referred_id)]
        self.db.set("pending_referrals", pending_referrals)
        
        # معالجة الدعوة
        return self.process_referral(int(referrer_id), referred_id)