# verification_system.py المطور لـ ᴋʏᴀɴ sɪᴍ_ʙᴏᴛ
import random


class VerificationSystem:
    def __init__(self, db):
        self.db = db
        if not db.exists("verified_users"):
            db.set("verified_users", [])
        if not db.exists("verification_sessions"):
            db.set("verification_sessions", {})

    def generate_math_question(self):
        """إنشاء سؤال رياضي سهل جداً (مستوى أولى ابتدائي) لـ ᴋɪᴀɴ"""
        # نختار أرقام بسيطة جداً من 1 إلى 5 فقط
        num1 = random.randint(1, 5)
        num2 = random.randint(1, 5)

        operation = '+'  # نثبتها جمع عشان تكون أسهل شي
        answer = num1 + num2
        question = f"{num1} + {num2}"

        return question, answer

    def create_verification_session(self, user_id):
        """إنشاء جلسة تحقق جديدة للمستخدم"""
        question, answer = self.generate_math_question()

        sessions = self.db.get("verification_sessions")
        sessions[str(user_id)] = {
            "question": question,
            "answer": answer,
            "attempts": 0,
            "completed": False
        }
        self.db.set("verification_sessions", sessions)

        return question

    def verify_answer(self, user_id, user_answer):
        """التحقق من الإجابة مع رسائل طقطقة"""
        sessions = self.db.get("verification_sessions")
        user_session = sessions.get(str(user_id))

        if not user_session:
            return False, "⚠️ ما عندك جلسة تحقق.. أرسل /start"

        if user_session["completed"]:
            return True, "✅ أنت أصلاً آدمي ومتحقق مسبقاً!"

        try:
            user_answer = int(user_answer)
            correct_answer = user_session["answer"]

            if user_answer == correct_answer:
                user_session["completed"] = True
                sessions[str(user_id)] = user_session
                self.db.set("verification_sessions", sessions)

                verified_users = self.db.get("verified_users")
                if user_id not in verified_users:
                    verified_users.append(user_id)
                    self.db.set("verified_users", verified_users)

                return True, "كفو.. طلعت آدمي مش صيني! 😂✅"
            else:
                user_session["attempts"] += 1
                sessions[str(user_id)] = user_session
                self.db.set("verification_sessions", sessions)

                if user_session["attempts"] >= 3:
                    return False, "يا ساتر.. 3 محاولات غلط؟ شكل العلة فيك مش في البوت! 💀"
                else:
                    # رسالة طقطقة عند الخطأ
                    rem = 3 - user_session['attempts']
                    return False, f"يا ساتر.. حتى ذي صعبة عليك؟ 😂 باقي لك {rem} محاولات"

        except ValueError:
            return False, "يا ذكي أرسل رقم فقط.. لا تسوي فيها فيلسوف! 🤡"

    def is_user_verified(self, user_id):
        """التحقق مما إذا كان المستخدم قد أكمل التحقق"""
        verified_users = self.db.get("verified_users")
        return user_id in verified_users

    def cleanup_session(self, user_id):
        """تنظيف جلسة التحقق"""
        sessions = self.db.get("verification_sessions")
        if str(user_id) in sessions:
            del sessions[str(user_id)]
            self.db.set("verification_sessions", sessions)


def setup_verification_system(db):
    return VerificationSystem(db)