from telethon import Button
import re

# قاموس اللغات
LANGUAGES = {
    'ar': {
        'name': 'العربية 🇸🇦',
        'messages': {
            'START_MESSAGE':
                "مرحباً بك في ᴋʏᴀɲ sɪᴍ_ʙᴏᴛ \n"
                "📱︙متجر بيع  حسابات تيليجرام \n"
                "🆔︙ايديك : {}\n"
                "💰︙رصيدك : {} ﷼ (ريال سعودي)\n"
                "✅︙يرجى استخدام الأزرار التالية :",

            'ADMIN_MESSAGE': "**🚀︙ مرحباً بك عزيزي المالك**",

            'TRANSFER_MESSAGE':
                "**✅︙مرحباً بك عزيزي في قسم التحويل** \n"
                "♻️︙يتم التحويل إلى العضو المراد بالضبط \n"
                "👨‍✈️︙التحويل يكون آمناً بنسبة كبيرة \n"
                "〽️︙عمولة التحويل ↫ 2% \n"
                "**🆔︙قم بإرسال ايدي العضو المراد تحويل الفلوس إليه : **",

            'BUY_MESSAGE':
                "**✅︙هل أنت متأكد من شراء الرقم؟**\n"
                "**- ⚠️ تنبيه هام** عندما تقوم بتأكيد الشراء سيتم خصم سعر الرقم من رصيدك ولا يمكنك إرجاع الرصيد أو التعويض إلا في حال لم يصلك كود التفعيل وفي حال واجهت مشكلة تواصل مع الدعم"
                "\n ⌁︙معلومات الرقم :-"
                "\n"
                "🌎︙ الدولة: {}\n"
                "💰︙ سعر الرقم : {} ﷼ (سعودي)\n"
                "**🚀︙إذا كنت تريد الشراء اضغط (تأكيد ✅) و إذا لا تريد اضغط (إلغاء ❌)**",

            'COUNTRY_LIST':
                "🌐︙**قم باختيار الدولة التي تريد الشراء منها**.\n\n"
                "**☎️ : حسابات جاهزه للتسجيل في تيليجرام**",

            'TRUST_MESSAGE':
                "**- تم شراء حساب جديد من البوت 📢**\n\n"
                "🏳 - الدولة : {}\n"
                "❇️ - المنصة : تليجرام 💙\n"
                "☎️ - الرقم : +{}...\n"
                "💰 - السعر : {} ﷼ ريال سعودي\n"
                "🆔 - العميل : {}...\n"
                "📥 - كود التفعيل : `{}`\n"
                "🛠 الحالة : تم التفعيل ✅\n\n"
                "📆 التاريخ و الوقت : {}",

            'RECHARGE_MESSAGE':
                "⌯ تستطيع شحن حسابك الان عبر:\n\n"
                "•  تحويل بنوك السعودية \n"
                "• لايك كارد - بطايق سوا \n"
                "• بينانس | Binance  ( تلقائي )\n"
                "• عملات رقمية USDT - LTC - TON",

            'CONTACT_ADMIN_MESSAGE':
                "**👨‍💻︙اتصل بالمسؤول للشحن:**\n\n"
                "• المسؤول: {}\n\n"
                "**📝︙تعليمات الشحن:**\n"
                "1. اضغط على الزر أدناه للتواصل مباشرة\n"
                "2. اكتب رسالتك مع إثبات الدفع\n"
                "3. انتظر تأكيد الشحن من المسؤول",



            'RULES_MESSAGE': "⚖️︙ قوانين ᴋʏᴀɲ sɪᴍ_ʙᴏᴛ: 1-التعويض فقط إذا لم يصل الكود 2-أنت مسؤول عن خصوصية رقمك بعد التفعيل 3-الرصيد لا يسترد ككاش 4-الاحترام شرط أساسي للدعم ⚠️ بمجرد استخدامك للبوت فأنت توافق على الشروط.",
            'LANGUAGE_CHANGED_MESSAGE': "✅︙تم تغيير اللغة إلى العربية.",
            'CHOOSE_LANGUAGE_MESSAGE': "**🌐︙اختر اللغة:**",

            # أزرار القائمة الرئيسية
            'FRAUD_BUTTON': "🚨 حسابات احتيالية",
            'FAKE_BUTTON': "🤖 حسابات مزيفة",
            'OLD_BUTTON': "📦 حسابات إنشاء قديم",
            'SELL_BUTTON': "- بيع رقم .",
            'BUY_BUTTON': "🛒 شراء رقم",
            'RECHARGE_BUTTON': "💳 شحن رصيد",
            'TRANSFER_BUTTON': "🔄 تحويل رصيد",
            'RULES_BUTTON': "📜 القوانين",
            'CURRENCY_BUTTON': "💱 تغيير العملة",
            'LANGUAGE_BUTTON': "🌐 تغيير اللغة",
            'BACK_BUTTON': "🔙 رجوع",
            'SETTINGS_MENU_BUTTON': "⚙️ الإعدادات",
            'SETTINGS_MENU_MESSAGE': "**⚙️︙قائمة الإعدادات**\n\nاختر ما تريد تعديله:",

            # الأزرار الجديدة
            'OFFICIAL_CHANNEL_BUTTON': "📢 القناة الرسمية",
            'ACTIVATIONS_CHANNEL_BUTTON': "✅ قناة التفعيلات",
            'SUPPORT_BUTTON': "🛠️ الدعم الفني",

            # رسائل الأزرار الجديدة
            'OFFICIAL_CHANNEL_MESSAGE': "**📢︙القناة الرسمية للبوت**\n\n- تابع آخر التحديثات والإعلانات الهامة\n- شروحات استخدام البوت\n- عروض خاصة وحصرية\n\n🔗 https://t.me/QQQ_4i",
            'ACTIVATIONS_CHANNEL_MESSAGE': "**🔔︙قناة التفعيلات والإثباتات**\n\n- تابع آخر التفعيلات الناجحة\n- شاهد إثباتات التسليم للعملاء\n- تأكد من مصداقية البوت\n\n🔗 https://t.me/QQQ_5i",
            'SUPPORT_MESSAGE': "🛠️︙الدعم الفني\n\n1️⃣ @mYJYQD\n2️⃣ @FF_1i\n\n**📝︙اضغط على أحد الحسابات أعلاه للتواصل مع الدعم الفني**",

            # رسائل وأزرار جديدة
            'SOLD_ACCOUNTS_BUTTON': "- الأرقام المباعة",
            'SETTINGS_BUTTON': "- إعدادات الأرقام",
            'FORCE_SUB_BUTTON': "- الاشتراك الإجباري",
            'ADMINS_BUTTON': "- قسم الأدمنية",
            'BUY_SELL_BUTTON': "- قسم البيع و الشراء",
            'BALANCE_BUTTON': "- قسم الرصيد",
            'BAN_BUTTON': "- قسم الحظر",
            'TRUST_CHANNEL_BUTTON': "- قناة إثباتات التسليم",
            'EDIT_RULES_BUTTON': "- تعديل رسالة القوانين",

            # رسائل جديدة
            'SOLD_ACCOUNTS_LIST': "**📋︙قائمة الأرقام المباعة:**",
            'NO_SOLD_ACCOUNTS': "**⚠️︙لا توجد أرقام مباعة حالياً**",
            'SOLD_ACCOUNT_DETAILS': "**📄︙تفاصيل الرقم المباع:**\n\n📞 الرقم: +{}\n🌎 الدولة: {}\n💰 السعر: {} ﷼ ريال سعودي\n👤 البائع: {}\n🔄 الحالة: {}",
            'GET_CODE_BUTTON': "- الحصول على الكود",
            'ADD_TO_SALE_BUTTON': "- إضافة للبيع",
            'DELETE_SOLD_BUTTON': "- حذف الرقم",
            'ACCOUNT_NOT_FOUND': "❌︙لم يتم العثور على الحساب",
            'CODE_FOUND': "**✅︙تم العثور على الكود:**\n\n📞 الرقم: `{}`\n🔐 التحقق بخطوتين: `{}`\n📨 الكود: `{}`\n\nتم إيجاد الكود بنجاح",
            'CODE_NOT_FOUND': "**❌︙لم يتم العثور على الكود:**\n\n📞 الرقم: `{}`\n🔐 التحقق بخطوتين: `{}`\n\nلم يصل الكود بعد؟ يمكنك طلب كود جديد",
            'ACCOUNT_ADDED_TO_SALE': "✅︙تم إضافة الرقم للبيع بنجاح",
            'ACCOUNT_ADDED_SUCCESS': "**✅︙تم إضافة الرقم للبيع بنجاح**\n\nيمكن الآن للمستخدمين شراء هذا الرقم من قسم شراء رقم",
            'ACCOUNT_DELETED': "✅︙تم حذف الرقم بنجاح",
            'ACCOUNT_DELETED_SUCCESS': "**✅︙تم حذف الرقم من قائمة الأرقام المباعة**",
            'ACCOUNT_ALREADY_ADDED': "⚠️︙هذا الرقم مضاف بالفعل للبيع",
            'PENDING_STATUS': "في انتظار المعالجة",
            'ADDED_TO_SALE_STATUS': "مضاف للبيع",
            'RETRY_CODE_BUTTON': "طلب كود جديد",
            'ACCESS_DENIED': "⛔︙ليس لديك صلاحية الوصول لهذا القسم",
            'TOTAL_ACCOUNTS': "**إجمالي أرقام البوت: {}**\n\n",
            'COUNTRY_ACCOUNTS': "- {}: {} رقم\n",
            'PLEASE_WAIT': "- برجاء الانتظار ...",

            # رسائل نظام التخزين
            'STORAGE_BUTTON': "- قسم التخزين",
            'STORAGE_MENU_MESSAGE': "**📦︙قسم تخزين الأرقام**\n\n• إجمالي الأرقام: {total_numbers}\n• الأرقام المخزنة: {stored_numbers}\n• الأرقام المعروضة للبيع: {selling_numbers}",
            'VIEW_STORED_NUMBERS': "- عرض الأرقام المخزنة",
            'AUTO_SELL_SETTINGS': "- إعدادات البيع التلقائي",
            'STORED_NUMBERS_LIST': "**📋︙الأرقام المخزنة**\n\nإجمالي الأرقام: {total}\nعرض {start}-{end}",
            'NO_STORED_NUMBERS': "**⚠️︙لا توجد أرقام مخزنة حالياً**",
            'NUMBER_MANAGEMENT_MESSAGE': "**📱︙إدارة الرقم**\n\n📞 الرقم: +{phone}\n🌎 الدولة: {country}\n💰 السعر: {price} ﷼ ريال سعودي\n🔄 الحالة: {status}\n👤 البائع: {seller}",
            'ADD_TO_SELLING_BUTTON': "- إضافة للبيع",
            'REMOVE_FROM_SELLING_BUTTON': "- إزالة من البيع",
            'DELETE_NUMBER_BUTTON': "- حذف الرقم",
            'CODE_RETRIEVED_MESSAGE': "**✅︙تم استرجاع الكود**\n\n📞 الرقم: +{phone}\n📨 الكود: `{code}`",
            'CODE_NOT_FOUND_MESSAGE': "**❌︙لم يتم العثور على الكود**\n\n📞 الرقم: +{phone}",
            'BACK_TO_MANAGEMENT': "⦉ العودة للإدارة",
            'ENABLED': "مفعل",
            'DISABLED': "معطل",
            'AUTO_SELL_SETTINGS_MESSAGE': "**⚙️︙إعدادات البيع التلقائي**\n\nالحالة: {status}",
            'ENABLE_AUTO_SELL': "- تفعيل البيع التلقائي",
            'DISABLE_AUTO_SELL': "- تعطيل البيع التلقائي",
            'NUMBER_ADDED_TO_SELLING': "✅︙تم إضافة الرقم للبيع",
            'NUMBER_REMOVED_FROM_SELLING': "✅︙تم إزالة الرقم من البيع",
            'DELETE_CONFIRM_MESSAGE': "**⚠️︙تأكيد الحذف**\n\nهل أنت متأكد من حذف الرقم +{}؟",
            'DELETE_SUCCESS_MESSAGE': "✅︙تم حذف الرقم بنجاح",
            'STATUS_STORED': "مخزن",
            'STATUS_SELLING': "معروض للبيع",
            'STATUS_SOLD': "تم بيعه",

            # رسائل نظام الإحالة الجديد
            'REFERRAL_BUTTON': "🎁 نظام الإحالة",
            'REFERRAL_MENU_MESSAGE': "**🎁︙نظام الإحالة**\n\n• مكافأة كل دعوة: {reward} ﷼ ريال سعودي\n• عدد المدعوين: {total_referred}\n• إجمالي الأرباح: {total_earned} ﷼ ريال سعودي",
            'REFERRAL_LINK_MESSAGE': "**📎︙رابط الدعوة الخاص بك:**\n\n`{link}`\n\nشارك هذا الرابط مع أصدقائك واحصل على {reward} ﷼ ريال سعودي لكل صديق ينضم!",
            'REFERRAL_STATS_MESSAGE': "**📊︙إحصائيات الدعوة**\n\n• عدد المدعوين: {total_referred}\n• إجمالي الأرباح: {total_earned} ﷼ ريال سعودي\n• مكافأة كل دعوة: {reward} ﷼ ريال سعودي",
            'NO_REFERRED_USERS': "⚠️︙لم تقم بدعوة أي مستخدم حتى الآن",

            'COUPON_BUTTON': "🎟️ كود خصم",
            'ENTER_COUPON': "✍️︙أرسل كود الخصم:",
            'COUPON_SUCCESS': "✅︙تم تطبيق الخصم: {}%",
            'COUPON_INVALID': "❌︙كود غير صالح",
        }
    },
    'en': {
        'name': 'English 🇺🇸',
        'messages': {
            'START_MESSAGE':
                "Welcome to ᴋʏᴀɲ sɪᴍ_ʙᴏᴛ \n"
                "📱︙Telegram Account Selling & Buying Bot \n"
                "🆔︙Your ID : `{}`\n"
                "💰︙Your Balance : {} (Saudi Riyal)\n"
                "✅︙Please use the following buttons :",

            'ADMIN_MESSAGE': "**🚀︙ Welcome, Owner**",

            'TRANSFER_MESSAGE':
                "**✅︙Welcome to the transfer section** \n"
                "♻️︙Transfer to the desired member exactly \n"
                "👨‍✈️︙Transfer is highly secure \n"
                "〽️︙Transfer commission ↫ 2% \n"
                "**🆔︙Send the ID of the member you want to transfer money to : **",

            'BUY_MESSAGE':
                "**✅︙Are you sure you want to buy the number?**\n"
                "**- ⚠️ Important notice** When you confirm the purchase, the number price will be deducted from your balance and you cannot refund the balance or get compensation unless the activation code does not arrive"
                "\n ⌁︙Number information :-"
                "\n"
                "🌎︙ Country: {}\n"
                "💰︙ Number price : {}﷼ (Saudi Riyal)\n"
                "**🚀︙If you want to buy press (Confirm ✅) and if not press (Cancel ❌)**",

            'COUNTRY_LIST':
                "🌐︙**Choose the country you want to buy from**.\n\n"
                "**☎️ : Ready accounts for registration in Telegram**",

            'TRUST_MESSAGE':
                "**- A new account has been purchased from the bot 📢**\n\n"
                "🏳 - Country : {}\n"
                "❇️ - Platform : Telegram 💙\n"
                "☎️ - Number : +{}...\n"
                "💰 - Price : {} SAR\n"
                "🆔 - Client : {}...\n"
                "📥 - Activation code : `{}`\n"
                "🛠 Status : Activated ✅\n\n"
                "📆 Date and Time : {}",

            'RECHARGE_MESSAGE':
                "**🙋‍♂ ⌯ You can recharge your account now via:**\n\n"
                "• 🌀 #Kareemy_transfer_deposit\n"
                "• 🌀 #Jeeb_wallet_transfer\n"
                "• 🌀 #TON\n",

            'CONTACT_ADMIN_MESSAGE':
                "**👨‍💻︙Contact the administrator for recharge:**\n\n"
                "• Administrator: {}\n\n"
                "**📝︙Recharge instructions:**\n"
                "1. Click the button below to contact directly\n"
                "2. Write your message with payment proof\n"
                "3. Wait for recharge confirmation from the administrator",



            'RULES_MESSAGE': "Hello dear, you must adhere to the following rules:\n\n1. Do not post inappropriate content.\n2. Do not use the bot for illegal purposes.\n3. You must be patient and respectful in dealing with others.\n4. In case of a problem, contact technical support.",

            'LANGUAGE_CHANGED_MESSAGE': "✅︙Language changed to English.",
            'CHOOSE_LANGUAGE_MESSAGE': "**🌐︙Choose language:**",

            # Main menu buttons
            'SELL_BUTTON': "- Sell Number 📲.",
            'BUY_BUTTON': "- Buy Number 📱.",
            'RECHARGE_BUTTON': "- Recharge Balance 💰.",
            'TRANSFER_BUTTON': "- Transfer Balance ♻️.",
            'RULES_BUTTON': "- Disclaimer 📵.",
            'CURRENCY_BUTTON': "- Change Currency 💱.",
            'LANGUAGE_BUTTON': "- Change Language 🌐.",
            'BACK_BUTTON': "⦉ Back ⬅️ ⦊",
            'SETTINGS_MENU_BUTTON': "- Settings ⚙️",
            'SETTINGS_MENU_MESSAGE': "**⚙️︙Settings Menu**\n\nChoose what you want to edit:",

            # New buttons
            'OFFICIAL_CHANNEL_BUTTON': "- Official Channel 📢",
            'ACTIVATIONS_CHANNEL_BUTTON': "- Activations Channel 🔔",
            'SUPPORT_BUTTON': "- Contact Support 👨‍💻",

            # New button messages
            'OFFICIAL_CHANNEL_MESSAGE': "**📢︙Bot Official Channel**\n\n- Follow the latest updates and important announcements\n- Bot usage tutorials\n- Special and exclusive offers",
            'ACTIVATIONS_CHANNEL_MESSAGE': "**🔔︙Activations and Proofs Channel**\n\n- Follow successful activations\n- Watch delivery proofs for customers\n- Verify bot credibility",
            'SUPPORT_MESSAGE': "**👨‍💻︙Customer Support**\n\n- For inquiries and complaints\n- For technical assistance\n- For development suggestions",

            # New messages and buttons
            'SOLD_ACCOUNTS_BUTTON': "- Sold Accounts 📋",
            'SETTINGS_BUTTON': "- Number Settings 🚀",
            'FORCE_SUB_BUTTON': "- Force Subscription 〽️",
            'ADMINS_BUTTON': "- Admins Section 👨‍✈️",
            'BUY_SELL_BUTTON': "- Buy & Sell Section 💰",
            'BALANCE_BUTTON': "- Balance Section 🤍",
            'BAN_BUTTON': "- Ban Section 🚫",
            'TRUST_CHANNEL_BUTTON': "- Trust Channel 🖤",
            'EDIT_RULES_BUTTON': "- Edit Rules 🔐",

            # New messages
            'SOLD_ACCOUNTS_LIST': "**📋︙Sold Accounts List:**",
            'NO_SOLD_ACCOUNTS': "**⚠️︙No sold accounts currently**",
            'SOLD_ACCOUNT_DETAILS': "**📄︙Sold Account Details:**\n\n📞 Number: +{}\n🌎 Country: {}\n💰 Price: {} SAR\n👤 Seller: {}\n🔄 Status: {}",
            'GET_CODE_BUTTON': "- Get Code 📨",
            'ADD_TO_SALE_BUTTON': "- Add to Sale 🏷️",
            'DELETE_SOLD_BUTTON': "- Delete Account 🗑️",
            'ACCOUNT_NOT_FOUND': "❌︙Account not found",
            'CODE_FOUND': "**✅︙Code Found:**\n\n📞 Number: `{}`\n🔐 Two-Step: `{}`\n📨 Code: `{}`\n\nCode found successfully",
            'CODE_NOT_FOUND': "**❌︙Code Not Found:**\n\n📞 Number: `{}`\n🔐 Two-Step: `{}`\n\nCode not received yet? You can request a new code",
            'ACCOUNT_ADDED_TO_SALE': "✅︙Account added to sale successfully",
            'ACCOUNT_ADDED_SUCCESS': "**✅︙Account added to sale successfully**\n\nUsers can now purchase this number from the buy section",
            'ACCOUNT_DELETED': "✅︙Account deleted successfully",
            'ACCOUNT_DELETED_SUCCESS': "**✅︙Account deleted from sold accounts list**",
            'ACCOUNT_ALREADY_ADDED': "⚠️︙This account is already added for sale",
            'PENDING_STATUS': "Pending",
            'ADDED_TO_SALE_STATUS': "Added to sale",
            'RETRY_CODE_BUTTON': "🔄 Request New Code",
            'ACCESS_DENIED': "⛔︙You don't have access to this section",
            'TOTAL_ACCOUNTS': "**Total Bot Accounts: {}**\n\n",
            'COUNTRY_ACCOUNTS': "- {}: {} numbers\n",
            'PLEASE_WAIT': "- Please wait ...",

            # Storage system messages
            'STORAGE_BUTTON': "- Storage Section 📦",
            'STORAGE_MENU_MESSAGE': "**📦︙Storage Section**\n\n• Total Numbers: {total_numbers}\n• Stored Numbers: {stored_numbers}\n• Selling Numbers: {selling_numbers}",
            'VIEW_STORED_NUMBERS': "- View Stored Numbers 📋",
            'AUTO_SELL_SETTINGS': "- Auto Sell Settings ⚙️",
            'STORED_NUMBERS_LIST': "**📋︙Stored Numbers**\n\nTotal Numbers: {total}\nShowing {start}-{end}",
            'NO_STORED_NUMBERS': "**⚠️︙No stored numbers currently**",
            'NUMBER_MANAGEMENT_MESSAGE': "**📱︙Number Management**\n\n📞 Number: +{phone}\n🌎 Country: {country}\n💰 Price: {price} SAR\n🔄 Status: {status}\n👤 Seller: {seller}",
            'ADD_TO_SELLING_BUTTON': "- Add to Selling 🏷️",
            'REMOVE_FROM_SELLING_BUTTON': "- Remove from Selling ❌",
            'DELETE_NUMBER_BUTTON': "- Delete Number 🗑️",
            'CODE_RETRIEVED_MESSAGE': "**✅︙Code Retrieved**\n\n📞 Number: +{phone}\n📨 Code: `{code}`",
            'CODE_NOT_FOUND_MESSAGE': "**❌︙Code Not Found**\n\n📞 Number: +{phone}",
            'BACK_TO_MANAGEMENT': "⦉ Back to Management ⬅️",
            'ENABLED': "Enabled",
            'DISABLED': "Disabled",
            'AUTO_SELL_SETTINGS_MESSAGE': "**⚙️︙Auto Sell Settings**\n\nStatus: {status}",
            'ENABLE_AUTO_SELL': "- Enable Auto Sell ✅",
            'DISABLE_AUTO_SELL': "- Disable Auto Sell ❌",
            'NUMBER_ADDED_TO_SELLING': "✅︙Number added to selling",
            'NUMBER_REMOVED_FROM_SELLING': "✅︙Number removed from selling",
            'DELETE_CONFIRM_MESSAGE': "**⚠️︙Delete Confirmation**\n\nAre you sure you want to delete number +{}?",
            'DELETE_SUCCESS_MESSAGE': "✅︙Number deleted successfully",
            'STATUS_STORED': "Stored",
            'STATUS_SELLING': "Selling",
            'STATUS_SOLD': "Sold",

            # New referral system messages
            'REFERRAL_BUTTON': "- Referral System 🎁",
            'REFERRAL_MENU_MESSAGE': "**🎁︙Referral System**\n\n• Reward per referral: {reward} SAR\n• Total referred: {total_referred}\n• Total earned: {total_earned} SAR",
            'REFERRAL_LINK_MESSAGE': "**📎︙Your Referral Link:**\n\n`{link}`\n\nShare this link with friends and get {reward} SAR for each friend who joins!",
            'REFERRAL_STATS_MESSAGE': "**📊︙Referral Statistics**\n\n• Total referred: {total_referred}\n• Total earned: {total_earned} SAR\n• Reward per referral: {reward} SAR",
            'NO_REFERRED_USERS': "⚠️︙You haven't referred any users yet",
        }
    },
    'fa': {
        'name': 'فارسی 🇮🇷',
        'messages': {
            'START_MESSAGE':
                "به ربات ᴋʏᴀɲ sɪᴍ_ʙᴏᴛ خوش آمدید \n"
                "📱︙ربات خریدوفروش حسابات تلگرام \n"
                "🆔︙آیدی شما : `{}`\n"
                "💰︙موجودی شما : {} (ریال سعودی)\n"
                "✅︙لطفاً از دکمه های زیر استفاده کنید :",

            'ADMIN_MESSAGE': "**🚀︙ به بخش مدیریت خوش آمدید**",

            'TRANSFER_MESSAGE':
                "**✅︙به بخش انتقال وجه خوش آمدید** \n"
                "♻️︙انتقال وجه دقیقاً به عضو مورد نظر انجام می شود \n"
                "👨‍✈️︙انتقال وجه بسیار امن است \n"
                "〽️︙کارمزد انتقال ↫ 2% \n"
                "**🆔︙آیدی عضوی که می خواهید پول به او انتقال دهید را ارسال کنید : **",

            'BUY_MESSAGE':
                "**✅︙آیا از خرید شماره مطمئن هستید؟**\n"
                "**- ⚠️ هشدار مهم** هنگام تأیید خرید، قیمت شماره از موجودی شما کسر می شود و نمی توانید موجودی را بازگردانید یا جبران کنید مگر در صورتی که کد فعال سازی نرسد"
                "\n ⌁︙اطلاعات شماره :-"
                "\n"
                "🌎︙ کشور: {}\n"
                "💰︙ قیمت شماره : {}﷼ (ریال سعودی)\n"
                "**🚀︙اگر می خواهید خرید کنید (تأیید ✅) و اگر نمی خواهید (لغو ❌) را فشار دهید**",

            'COUNTRY_LIST':
                "🌐︙**کشوری که می خواهید از آن خرید کنید را انتخاب کنید**.\n\n"
                "**☎️ : اکانت های آماده برای ثبت نام در تلگرام**",

            'TRUST_MESSAGE':
                "**- یک اکانت جدید از ربات خریداری شد 📢**\n\n"
                "🏳 - کشور : {}\n"
                "❇️ - پلتفرم : تلگرام 💙\n"
                "☎️ - شماره : +{}...\n"
                "💰 - قیمت : {} ریال سعودی\n"
                "🆔 - مشتری : {}...\n"
                "📥 - کد فعال سازی : `{}`\n"
                "🛠 وضعیت : فعال شد ✅\n\n"
                "📆 تاریخ و زمان : {}",

            'RECHARGE_MESSAGE':
                "**🙋‍♂ ⌯ هم اکنون می توانید حساب خود را شارژ کنید:**\n\n"
                "• 🌀 #انتقال_کریمی_و_واریز\n"
                "• 🌀 #انتقال_کیف_پول_جیب\n"
                "• 🌀 #تون_TON\n",

            'CONTACT_ADMIN_MESSAGE':
                "**👨‍💻︙برای شارژ با مدیر تماس بگیرید:**\n\n"
                "• مدیر: {}\n\n"
                "**📝︙دستورالعمل های شارژ:**\n"
                "1. برای تماس مستقیم روی دکمه زیر کلیک کنید\n"
                "2. پیام خود را با اثبات پرداخت بنویسید\n"
                "3. منتظر تأیید شارژ از مدیر باشید",



            'RULES_MESSAGE': "سلام عزیز، شما باید قوانین زیر را رعایت کنید:\n\n1. محتوای نامناسب منتشر نکنید.\n2. از ربات برای اهداف غیرقانونی استفاده نکنید.\n3. باید در برخورد با دیگران صبور و محترم باشید.\n4. در صورت وجود مشکل، با پشتیبانی فنی تماس بگیرید.",

            'LANGUAGE_CHANGED_MESSAGE': "✅︙زبان به فارسی تغییر یافت.",
            'CHOOSE_LANGUAGE_MESSAGE': "**🌐︙زبان را انتخاب کنید:**",

            'SELL_BUTTON': "- فروش شماره 📲.",
            'BUY_BUTTON': "- خرید شماره 📱.",
            'RECHARGE_BUTTON': "- شارژ موجودی 💰.",
            'TRANSFER_BUTTON': "- انتقال موجودی ♻️.",
            'RULES_BUTTON': "- سلب مسئولیت 📵.",
            'CURRENCY_BUTTON': "- تغییر ارز 💱.",
            'LANGUAGE_BUTTON': "- تغییر زبان 🌐.",
            'BACK_BUTTON': "⦉ بازگشت ⬅️ ⦊",
            'SETTINGS_MENU_BUTTON': "- تنظیمات ⚙️",
            'SETTINGS_MENU_MESSAGE': "**⚙️︙منوی تنظیمات**\n\nآنچه را که می خواهید ویرایش کنید انتخاب کنید:",

            'OFFICIAL_CHANNEL_BUTTON': "- کانال رسمی 📢",
            'ACTIVATIONS_CHANNEL_BUTTON': "- کانال فعال سازی ها 🔔",
            'SUPPORT_BUTTON': "- تماس با پشتیبانی 👨‍💻",

            'OFFICIAL_CHANNEL_MESSAGE': "**📢︙کانال رسمی ربات**\n\n- آخرین به روز رسانی ها و اطلاعیه های مهم را دنبال کنید\n- آموزش های استفاده از ربات\n- پیشنهادات ویژه و انحصاری",
            'ACTIVATIONS_CHANNEL_MESSAGE': "**🔔︙کانال فعال سازی ها و اثبات ها**\n\n- آخرین فعال سازی های موفق را دنبال کنید\n- اثبات های تحویل به مشتریان را مشاهده کنید\n- از اعتبار ربات اطمینان حاصل کنید",
            'SUPPORT_MESSAGE': "**👨‍💻︙پشتیبانی مشتریان**\n\n- برای سوالات و شکایات\n- برای کمک فنی\n- برای پیشنهادات توسعه",

            'SOLD_ACCOUNTS_BUTTON': "- اکانت های فروخته شده 📋",
            'SETTINGS_BUTTON': "- تنظیمات شماره 🚀",
            'FORCE_SUB_BUTTON': "- اشتراک اجباری 〽️",
            'ADMINS_BUTTON': "- بخش ادمین ها 👨‍✈️",
            'BUY_SELL_BUTTON': "- بخش خرید و فروش 💰",
            'BALANCE_BUTTON': "- بخش موجودی 🤍",
            'BAN_BUTTON': "- بخش مسدودی 🚫",
            'TRUST_CHANNEL_BUTTON': "- کانال اثبات تحویل 🖤",
            'EDIT_RULES_BUTTON': "- ویرایش پیام قوانین 🔐",

            'SOLD_ACCOUNTS_LIST': "**📋︙لیست اکانت های فروخته شده:**",
            'NO_SOLD_ACCOUNTS': "**⚠️︙هیچ اکانت فروخته شده ای در حال حاضر وجود ندارد**",
            'SOLD_ACCOUNT_DETAILS': "**📄︙جزئیات اکانت فروخته شده:**\n\n📞 شماره: +{}\n🌎 کشور: {}\n💰 قیمت: {} $\n👤 فروشنده: {}\n🔄 وضعیت: {}",
            'GET_CODE_BUTTON': "- دریافت کد 📨",
            'ADD_TO_SALE_BUTTON': "- اضافه به فروش",
            'DELETE_SOLD_BUTTON': "- حذف اکانت 🗑️",
            'ACCOUNT_NOT_FOUND': "❌︙اکانت پیدا نشد",
            'CODE_FOUND': "**✅︙کد پیدا شد:**\n\n📞 شماره: `{}`\n🔐 دو مرحله ای: `{}`\n📨 کد: `{}`\n\nکد با موفقیت پیدا شد",
            'CODE_NOT_FOUND': "**❌︙کد پیدا نشد:**\n\n📞 شماره: `{}`\n🔐 دو مرحله ای: `{}`\n\nکد هنوز نرسیده؟ می توانید کد جدید درخواست کنید",
            'ACCOUNT_ADDED_TO_SALE': "✅︙اکانت با موفقیت به فروش اضافه شد",
            'ACCOUNT_ADDED_SUCCESS': "**✅︙اکانت با موفقیت به فروش اضافه شد**\n\nکاربران اکنون می توانند این شماره را از بخش خرید خریداری کنند",
            'ACCOUNT_DELETED': "✅︙اکانت با موفقیت حذف شد",
            'ACCOUNT_DELETED_SUCCESS': "**✅︙اکانت از لیست اکانت های فروخته شده حذف شد**",
            'ACCOUNT_ALREADY_ADDED': "⚠️︙این اکانت قبلاً به فروش اضافه شده است",
            'PENDING_STATUS': "در انتظار پردازش",
            'ADDED_TO_SALE_STATUS': "اضافه شده به فروش",
            'RETRY_CODE_BUTTON': "🔄 درخواست کد جدید",
            'ACCESS_DENIED': "⛔︙شما دسترسی به این بخش را ندارید",
            'TOTAL_ACCOUNTS': "**مجموع اکانت های ربات: {}**\n\n",
            'COUNTRY_ACCOUNTS': "- {}: {} شماره\n",
            'PLEASE_WAIT': "- لطفاً منتظر بمانید ...",

            'STORAGE_BUTTON': "- بخش ذخیره سازی 📦",
            'STORAGE_MENU_MESSAGE': "**📦︙بخش ذخیره سازی**\n\n• مجموع شماره ها: {total_numbers}\n• شماره های ذخیره شده: {stored_numbers}\n• شماره های در حال فروش: {selling_numbers}",
            'VIEW_STORED_NUMBERS': "- مشاهده شماره های ذخیره شده 📋",
            'AUTO_SELL_SETTINGS': "- تنظیمات فروش خودکار ⚙️",
            'STORED_NUMBERS_LIST': "**📋︙شماره های ذخیره شده**\n\nمجموع شماره ها: {total}\nنمایش {start}-{end}",
            'NO_STORED_NUMBERS': "**⚠️︙هیچ شماره ذخیره شده ای در حال حاضر وجود ندارد**",
            'NUMBER_MANAGEMENT_MESSAGE': "**📱︙مدیریت شماره**\n\n📞 شماره: +{phone}\n🌎 کشور: {country}\n💰 قیمت: {price}$\n🔄 وضعیت: {status}\n👤 فروشنده: {seller}",
            'ADD_TO_SELLING_BUTTON': "- اضافه به فروش",
            'REMOVE_FROM_SELLING_BUTTON': "- حذف از فروش ❌",
            'DELETE_NUMBER_BUTTON': "- حذف شماره 🗑️",
            'CODE_RETRIEVED_MESSAGE': "**✅︙کد بازیابی شد**\n\n📞 شماره: +{phone}\n📨 کد: `{code}`",
            'CODE_NOT_FOUND_MESSAGE': "**❌︙کد پیدا نشد**\n\n📞 شماره: +{phone}",
            'BACK_TO_MANAGEMENT': "⦉ بازگشت به مدیریت ⬅️",
            'ENABLED': "فعال",
            'DISABLED': "غیرفعال",
            'AUTO_SELL_SETTINGS_MESSAGE': "**⚙️︙تنظیمات فروش خودکار**\n\nوضعیت: {status}",
            'ENABLE_AUTO_SELL': "- فعال کردن فروش خودکار ✅",
            'DISABLE_AUTO_SELL': "- غیرفعال کردن فروش خودکار ❌",
            'NUMBER_ADDED_TO_SELLING': "✅︙شماره به فروش اضافه شد",
            'NUMBER_REMOVED_FROM_SELLING': "✅︙شماره از فروش حذف شد",
            'DELETE_CONFIRM_MESSAGE': "**⚠️︙تأیید حذف**\n\nآیا از حذف شماره +{} مطمئن هستید؟",
            'DELETE_SUCCESS_MESSAGE': "✅︙شماره با موفقیت حذف شد",
            'STATUS_STORED': "ذخیره شده",
            'STATUS_SELLING': "در حال فروش",
            'STATUS_SOLD': "فروخته شده",

            'REFERRAL_BUTTON': "- سیستم دعوت 🎁",
            'REFERRAL_MENU_MESSAGE': "**🎁︙سیستم دعوت**\n\n• پاداش هر دعوت: {reward}$\n• تعداد دعوت شده ها: {total_referred}\n• مجموع درآمد: {total_earned}$",
            'REFERRAL_LINK_MESSAGE': "**📎︙لینک دعوت شما:**\n\n`{link}`\n\nاین لینک را با دوستان خود به اشتراک بگذارید و برای هر دوستی که عضو می شود {reward}$ دریافت کنید!",
            'REFERRAL_STATS_MESSAGE': "**📊︙آمار دعوت**\n\n• تعداد دعوت شده ها: {total_referred}\n• مجموع درآمد: {total_earned}$\n• پاداش هر دعوت: {reward}$",
            'NO_REFERRED_USERS': "⚠️︙شما هنوز هیچ کاربری را دعوت نکرده اید",
        }
    },
    'zh': {
        'name': '中文 🇨🇳',
        'messages': {
            'START_MESSAGE':
                "欢迎来到 ᴋʏɲ sɪᴍ_ʙᴏᴛ \n"
                "📱︙电报账户买卖机器人 \n"
                "🆔︙你的ID : `{}`\n"
                "💰︙你的余额 : {} (沙特里亚尔)\n"
                "✅︙请使用以下按钮 :",

            'ADMIN_MESSAGE': "**🚀︙ 欢迎，所有者**",

            'TRANSFER_MESSAGE':
                "**✅︙欢迎来到转账部分** \n"
                "♻️︙准确转账给所需成员 \n"
                "👨‍✈️︙转账非常安全 \n"
                "〽️︙转账佣金 ↫ 2% \n"
                "**🆔︙发送您要转账给的成员 ID : **",

            'BUY_MESSAGE':
                "**✅︙您确定要购买此号码吗？**\n"
                "**- ⚠️ 重要通知** 当您确认购买时，号码价格将从您的余额中扣除，除非激活码未到达，否则您无法退款或获得补偿"
                "\n ⌁︙号码信息 :-"
                "\n"
                "🌎︙ 国家: {}\n"
                "💰︙ 号码价格 : {}﷼ (沙特里亚尔)\n"
                "**🚀︙如果您想购买请按 (确认 ✅)，如果不想请按 (取消 ❌)**",

            'COUNTRY_LIST':
                "🌐︙**选择您要购买的国家**.\n\n"
                "**☎️ : 准备在 Telegram 注册的账户**",

            'TRUST_MESSAGE':
                "**- 从机器人购买了一个新账户 📢**\n\n"
                "🏳 - 国家 : {}\n"
                "❇️ - 平台 : Telegram 💙\n"
                "☎️ - 号码 : +{}...\n"
                "💰 - 价格 : $ {}\n"
                "🆔 - 客户 : {}...\n"
                "📥 - 激活码 : `{}`\n"
                "🛠 状态 : 已激活 ✅\n\n"
                "📆 日期和时间 : {}",

            'RECHARGE_MESSAGE':
                "**🙋‍♂ ⌯ 您现在可以通过以下方式充值账户:**\n\n"
                "• 🌀 #Kareemy转账存款\n"
                "• 🌀 #Jeeb钱包转账\n"
                "• 🌀 #TON\n",

            'CONTACT_ADMIN_MESSAGE':
                "**👨‍💻︙联系管理员充值:**\n\n"
                "• 管理员: {}\n\n"
                "**📝︙充值说明:**\n"
                "1. 点击下方按钮直接联系\n"
                "2. 写下您的消息并附上付款证明\n"
                "3. 等待管理员确认充值",

            'RULES_MESSAGE': "亲爱的用户，您必须遵守以下规则：\n\n1. 不要发布不当内容。\n2. 不要将机器人用于非法目的。\n3. 在与他人打交道时必须耐心和尊重。\n4. 如有问题，请联系技术支持。",

            'LANGUAGE_CHANGED_MESSAGE': "✅︙语言已更改为中文。",
            'CHOOSE_LANGUAGE_MESSAGE': "**🌐︙选择语言:**",

            'SELL_BUTTON': "- 出售号码 📲.",
            'BUY_BUTTON': "- 购买号码 📱.",
            'RECHARGE_BUTTON': "- 充值余额 💰.",
            'TRANSFER_BUTTON': "- 转账余额 ♻️.",
            'RULES_BUTTON': "- 免责声明 📵.",
            'CURRENCY_BUTTON': "- 更改货币 💱.",
            'LANGUAGE_BUTTON': "- 更改语言 🌐.",
            'BACK_BUTTON': "⦉ 返回 ⬅️ ⦊",
            'SETTINGS_MENU_BUTTON': "- 设置 ⚙️",
            'SETTINGS_MENU_MESSAGE': "**⚙️︙设置菜单**\n\n选择您要编辑的内容：",

            'OFFICIAL_CHANNEL_BUTTON': "- 官方频道 📢",
            'ACTIVATIONS_CHANNEL_BUTTON': "- 激活频道 🔔",
            'SUPPORT_BUTTON': "- 联系支持 👨‍💻",

            'OFFICIAL_CHANNEL_MESSAGE': "**📢︙机器人官方频道**\n\n- 关注最新更新和重要公告\n- 机器人使用教程\n- 特别和独家优惠",
            'ACTIVATIONS_CHANNEL_MESSAGE': "**🔔︙激活和证明频道**\n\n- 关注成功的激活\n- 查看给客户的交付证明\n- 验证机器人的可信度",
            'SUPPORT_MESSAGE': "**👨‍💻︙客户支持**\n\n- 用于查询和投诉\n- 用于技术协助\n- 用于开发建议",

            'SOLD_ACCOUNTS_BUTTON': "- 已售账户 📋",
            'SETTINGS_BUTTON': "- 号码设置 🚀",
            'FORCE_SUB_BUTTON': "- 强制订阅 〽️",
            'ADMINS_BUTTON': "- 管理员部分 👨‍✈️",
            'BUY_SELL_BUTTON': "- 买卖部分 💰",
            'BALANCE_BUTTON': "- 余额部分 🤍",
            'BAN_BUTTON': "- 封禁部分 🚫",
            'TRUST_CHANNEL_BUTTON': "- 信任频道 🖤",
            'EDIT_RULES_BUTTON': "- 编辑规则 🔐",

            'SOLD_ACCOUNTS_LIST': "**📋︙已售账户列表:**",
            'NO_SOLD_ACCOUNTS': "**⚠️︙当前没有已售账户**",
            'SOLD_ACCOUNT_DETAILS': "**📄︙已售账户详情:**\n\n📞 号码: +{}\n🌎 国家: {}\n💰 价格: {} SAR\n👤 卖家: {}\n🔄 状态: {}",
            'GET_CODE_BUTTON': "- 获取代码 📨",
            'ADD_TO_SALE_BUTTON': "- 添加到销售 🏷️",
            'DELETE_SOLD_BUTTON': "- 删除账户 🗑️",
            'ACCOUNT_NOT_FOUND': "❌︙未找到账户",
            'CODE_FOUND': "**✅︙找到代码:**\n\n📞 号码: `{}`\n🔐 两步验证: `{}`\n📨 代码: `{}`\n\n成功找到代码",
            'CODE_NOT_FOUND': "**❌︙未找到代码:**\n\n📞 号码: `{}`\n🔐 两步验证: `{}`\n\n代码尚未收到？您可以请求新代码",
            'ACCOUNT_ADDED_TO_SALE': "✅︙账户成功添加到销售",
            'ACCOUNT_ADDED_SUCCESS': "**✅︙账户成功添加到销售**\n\n用户现在可以从购买部分购买此号码",
            'ACCOUNT_DELETED': "✅︙账户成功删除",
            'ACCOUNT_DELETED_SUCCESS': "**✅︙账户已从已售账户列表中删除**",
            'ACCOUNT_ALREADY_ADDED': "⚠️︙此账户已添加到销售",
            'PENDING_STATUS': "待处理",
            'ADDED_TO_SALE_STATUS': "已添加到销售",
            'RETRY_CODE_BUTTON': "🔄 请求新代码",
            'ACCESS_DENIED': "⛔︙您无权访问此部分",
            'TOTAL_ACCOUNTS': "**机器人总账户: {}**\n\n",
            'COUNTRY_ACCOUNTS': "- {}: {} 个号码\n",
            'PLEASE_WAIT': "- 请稍候 ...",

            'STORAGE_BUTTON': "- 存储部分 📦",
            'STORAGE_MENU_MESSAGE': "**📦︙存储部分**\n\n• 总号码: {total_numbers}\n• 存储号码: {stored_numbers}\n• 销售号码: {selling_numbers}",
            'VIEW_STORED_NUMBERS': "- 查看存储号码 📋",
            'AUTO_SELL_SETTINGS': "- 自动销售设置 ⚙️",
            'STORED_NUMBERS_LIST': "**📋︙存储号码**\n\n总号码: {total}\n显示 {start}-{end}",
            'NO_STORED_NUMBERS': "**⚠️︙当前没有存储号码**",
            'NUMBER_MANAGEMENT_MESSAGE': "**📱︙号码管理**\n\n📞 号码: +{phone}\n🌎 国家: {country}\n💰 价格: {price}$\n🔄 状态: {status}\n👤 卖家: {seller}",
            'ADD_TO_SELLING_BUTTON': "- 添加到销售 🏷️",
            'REMOVE_FROM_SELLING_BUTTON': "- 从销售中移除 ❌",
            'DELETE_NUMBER_BUTTON': "- 删除号码 🗑️",
            'CODE_RETRIEVED_MESSAGE': "**✅︙代码已检索**\n\n📞 号码: +{phone}\n📨 代码: `{code}`",
            'CODE_NOT_FOUND_MESSAGE': "**❌︙未找到代码**\n\n📞 号码: +{phone}",
            'BACK_TO_MANAGEMENT': "⦉ 返回管理 ⬅️",
            'ENABLED': "已启用",
            'DISABLED': "已禁用",
            'AUTO_SELL_SETTINGS_MESSAGE': "**⚙️︙自动销售设置**\n\n状态: {status}",
            'ENABLE_AUTO_SELL': "- 启用自动销售 ✅",
            'DISABLE_AUTO_SELL': "- 禁用自动销售 ❌",
            'NUMBER_ADDED_TO_SELLING': "✅︙号码已添加到销售",
            'NUMBER_REMOVED_FROM_SELLING': "✅︙号码已从销售中移除",
            'DELETE_CONFIRM_MESSAGE': "**⚠️︙删除确认**\n\n您确定要删除号码 +{} 吗？",
            'DELETE_SUCCESS_MESSAGE': "✅︙号码成功删除",
            'STATUS_STORED': "已存储",
            'STATUS_SELLING': "销售中",
            'STATUS_SOLD': "已售出",

            'REFERRAL_BUTTON': "- 推荐系统 🎁",
            'REFERRAL_MENU_MESSAGE': "**🎁︙推荐系统**\n\n• 每次推荐奖励: {reward}$\n• 总推荐人数: {total_referred}\n• 总收入: {total_earned}$",
            'REFERRAL_LINK_MESSAGE': "**📎︙您的推荐链接:**\n\n`{link}`\n\n与朋友分享此链接，每有一位朋友加入即可获得 {reward}$！",
            'REFERRAL_STATS_MESSAGE': "**📊︙推荐统计**\n\n• 总推荐人数: {total_referred}\n• 总收入: {total_earned}$\n• 每次推荐奖励: {reward}$",
            'NO_REFERRED_USERS': "⚠️︙您尚未推荐任何用户",
        }
    },
    'ru': {
        'name': 'Русский 🇷🇺',
        'messages': {
            'START_MESSAGE':
                "Добро пожаловать в бота ᴋʏᴀɲ sɪᴍ_ʙᴏᴛ \n"
                "📱︙Бот по покупке и продаже учетных записей Telegram \n"
                "🆔︙Ваш ID : `{}`\n"
                "💰︙Ваш баланс : {} (Саудовский риял)\n"
                "✅︙Пожалуйста, используйте следующие кнопки :",

            'ADMIN_MESSAGE': "**🚀︙ Добро пожаловать, владелец**",

            'TRANSFER_MESSAGE':
                "**✅︙Добро пожаловать в раздел перевода** \n"
                "♻️︙Перевод точно нужному участнику \n"
                "👨‍✈️︙Перевод очень безопасен \n"
                "〽️︙Комиссия за перевод ↫ 2% \n"
                "**🆔︙Отправьте ID участника, которому хотите перевести деньги : **",

            'BUY_MESSAGE':
                "**✅︙Вы уверены, что хотите купить номер?**\n"
                "**- ⚠️ Важное уведомление** При подтверждении покупки цена номера будет вычтена из вашего баланса, и вы не можете вернуть баланс или получить компенсацию, если код активации не придет"
                "\n ⌁︙Информация о номере :-"
                "\n"
                "🌎︙ Страна: {}\n"
                "💰︙ Цена номера : {}﷼ (Саудовский риял)\n"
                "**🚀︙Если вы хотите купить, нажмите (Подтвердить ✅), если нет, нажмите (Отмена ❌)**",

            'COUNTRY_LIST':
                "🌐︙**Выберите страну, из которой хотите купить**.\n\n"
                "**☎️ : Готовые аккаунты для регистрации в Telegram**",

            'TRUST_MESSAGE':
                "**- Новая учетная запись была куплена у бота 📢**\n\n"
                "🏳 - Страна : {}\n"
                "❇️ - Платформа : Telegram 💙\n"
                "☎️ - Номер : +{}...\n"
                "💰 - Цена : $ {}\n"
                "🆔 - Клиент : {}...\n"
                "📥 - Код активации : `{}`\n"
                "🛠 Статус : Активирован ✅\n\n"
                "📆 Дата и время : {}",

            'RECHARGE_MESSAGE':
                "**🙋‍♂ ⌯ Вы можете пополнить свой счет сейчас через:**\n\n"
                "• 🌀 #Kareemy_перевод_депозит\n"
                "• 🌀 #Jeeb_кошелек_перевод\n"
                "• 🌀 #TON\n",

            'CONTACT_ADMIN_MESSAGE':
                "**👨‍💻︙Свяжитесь с администратором для пополнения:**\n\n"
                "• Администратор: {}\n\n"
                "**📝︙Инструкции по пополнению:**\n"
                "1. Нажмите на кнопку ниже для прямого контакта\n"
                "2. Напишите свое сообщение с подтверждением оплаты\n"
                "3. Ждите подтверждения пополнения от администратора",


            'RULES_MESSAGE': "Дорогой пользователь, вы должны соблюдать следующие правила:\n\n1. Не публикуйте неприемлемый контент.\n2. Не используйте бота для незаконных целей.\n3. Вы должны быть терпеливы и уважительны при общении с другими.\n4. При возникновении проблем свяжитесь со службой технической поддержки.",

            'LANGUAGE_CHANGED_MESSAGE': "✅︙Язык изменен на русский.",
            'CHOOSE_LANGUAGE_MESSAGE': "**🌐︙Выберите язык:**",

            'SELL_BUTTON': "- Продать номер 📲.",
            'BUY_BUTTON': "- Купить номер 📱.",
            'RECHARGE_BUTTON': "- Пополнить баланс 💰.",
            'TRANSFER_BUTTON': "- Перевести баланс ♻️.",
            'RULES_BUTTON': "- Отказ от ответственности 📵.",
            'CURRENCY_BUTTON': "- Изменить валюту 💱.",
            'LANGUAGE_BUTTON': "- Изменить язык 🌐.",
            'BACK_BUTTON': "⦉ Назад ⬅️ ⦊",
            'SETTINGS_MENU_BUTTON': "- Настройки ⚙️",
            'SETTINGS_MENU_MESSAGE': "**⚙️︙Меню настроек**\n\nВыберите, что вы хотите изменить:",

            'OFFICIAL_CHANNEL_BUTTON': "- Официальный канал 📢",
            'ACTIVATIONS_CHANNEL_BUTTON': "- Канал активаций 🔔",
            'SUPPORT_BUTTON': "- Связаться с поддержкой 👨‍💻",

            'OFFICIAL_CHANNEL_MESSAGE': "**📢︙Официальный канал бота**\n\n- Следите за последними обновлениями и важными объявлениями\n- Учебные пособия по использованию бота\n- Специальные и эксклюзивные предложения",
            'ACTIVATIONS_CHANNEL_MESSAGE': "**🔔︙Канал активаций и подтверждений**\n\n- Следите за успешными активациями\n- Смотрите подтверждения доставки клиентам\n- Убедитесь в надежности бота",
            'SUPPORT_MESSAGE': "**👨‍💻︙Поддержка клиентов**\n\n- Для запросов и жалоб\n- Для технической помощи\n- Для предложений по развитию",

            'SOLD_ACCOUNTS_BUTTON': "- Проданные аккаунты 📋",
            'SETTINGS_BUTTON': "- Настройки номера 🚀",
            'FORCE_SUB_BUTTON': "- Принудительная подписка 〽️",
            'ADMINS_BUTTON': "- Раздел администраторов 👨‍✈️",
            'BUY_SELL_BUTTON': "- Раздел покупки и продажи 💰",
            'BALANCE_BUTTON': "- Раздел баланса 🤍",
            'BAN_BUTTON': "- Раздел бана 🚫",
            'TRUST_CHANNEL_BUTTON': "- Канал доверия 🖤",
            'EDIT_RULES_BUTTON': "- Редактировать правила 🔐",

            'SOLD_ACCOUNTS_LIST': "**📋︙Список проданных аккаунтов:**",
            'NO_SOLD_ACCOUNTS': "**⚠️︙В настоящее время нет проданных аккаунтов**",
            'SOLD_ACCOUNT_DETAILS': "**📄︙Детали проданного аккаунта:**\n\n📞 Номер: +{}\n🌎 Страна: {}\n💰 Цена: {} SAR\n👤 Продавец: {}\n🔄 Статус: {}",
            'GET_CODE_BUTTON': "- Получить код 📨",
            'ADD_TO_SALE_BUTTON': "- Добавить в продажу 🏷️",
            'DELETE_SOLD_BUTTON': "- Удалить аккаунт 🗑️",
            'ACCOUNT_NOT_FOUND': "❌︙Аккаунт не найден",
            'CODE_FOUND': "**✅︙Код найден:**\n\n📞 Номер: `{}`\n🔐 Двухэтапная аутентификация: `{}`\n📨 Код: `{}`\n\nКод успешно найден",
            'CODE_NOT_FOUND': "**❌︙Код не найден:**\n\n📞 Номер: `{}`\n🔐 Двухэтапная аутентификация: `{}`\n\nКод еще не получен? Вы можете запросить новый код",
            'ACCOUNT_ADDED_TO_SALE': "✅︙Аккаунт успешно добавлен в продажу",
            'ACCOUNT_ADDED_SUCCESS': "**✅︙Аккаунт успешно добавлен в продажу**\n\nПользователи теперь могут купить этот номер из раздела покупки",
            'ACCOUNT_DELETED': "✅︙Аккаунт успешно удален",
            'ACCOUNT_DELETED_SUCCESS': "**✅︙Аккаунт удален из списка проданных аккаунтов**",
            'ACCOUNT_ALREADY_ADDED': "⚠️︙Этот аккаунт уже добавлен в продажу",
            'PENDING_STATUS': "В ожидании обработки",
            'ADDED_TO_SALE_STATUS': "Добавлен в продажу",
            'RETRY_CODE_BUTTON': "🔄 Запросить новый код",
            'ACCESS_DENIED': "⛔︙У вас нет доступа к этому разделу",
            'TOTAL_ACCOUNTS': "**Всего аккаунтов в боте: {}**\n\n",
            'COUNTRY_ACCOUNTS': "- {}: {} номеров\n",
            'PLEASE_WAIT': "- Пожалуйста, подождите ...",

            'STORAGE_BUTTON': "- Раздел хранения 📦",
            'STORAGE_MENU_MESSAGE': "**📦︙Раздел хранения**\n\n• Всего номеров: {total_numbers}\n• Сохраненные номера: {stored_numbers}\n• Номера в продаже: {selling_numbers}",
            'VIEW_STORED_NUMBERS': "- Просмотр сохраненных номеров 📋",
            'AUTO_SELL_SETTINGS': "- Настройки автоматической продажи ⚙️",
            'STORED_NUMBERS_LIST': "**📋︙Сохраненные номера**\n\nВсего номеров: {total}\nПоказано {start}-{end}",
            'NO_STORED_NUMBERS': "**⚠️︙В настоящее время нет сохраненных номеров**",
            'NUMBER_MANAGEMENT_MESSAGE': "**📱︙Управление номером**\n\n📞 Номер: +{phone}\n🌎 Страна: {country}\n💰 Цена: {price}$\n🔄 Статус: {status}\n👤 Продавец: {seller}",
            'ADD_TO_SELLING_BUTTON': "- Добавить в продажу 🏷️",
            'REMOVE_FROM_SELLING_BUTTON': "- Удалить из продажи ❌",
            'DELETE_NUMBER_BUTTON': "- Удалить номер 🗑️",
            'CODE_RETRIEVED_MESSAGE': "**✅︙Код получен**\n\n📞 Номер: +{phone}\n📨 Код: `{code}`",
            'CODE_NOT_FOUND_MESSAGE': "**❌︙Код не найден**\n\n📞 Номер: +{phone}",
            'BACK_TO_MANAGEMENT': "⦉ Назад к управлению ⬅️",
            'ENABLED': "Включено",
            'DISABLED': "Отключено",
            'AUTO_SELL_SETTINGS_MESSAGE': "**⚙️︙Настройки автоматической продажи**\n\nСтатус: {status}",
            'ENABLE_AUTO_SELL': "- Включить автоматическую продажу ✅",
            'DISABLE_AUTO_SELL': "- Отключить автоматическую продажу ❌",
            'NUMBER_ADDED_TO_SELLING': "✅︙Номер добавлен в продажу",
            'NUMBER_REMOVED_FROM_SELLING': "✅︙Номер удален из продажи",
            'DELETE_CONFIRM_MESSAGE': "**⚠️︙Подтверждение удаления**\n\nВы уверены, что хотите удалить номер +{}?",
            'DELETE_SUCCESS_MESSAGE': "✅︙Номер успешно удален",
            'STATUS_STORED': "Сохранен",
            'STATUS_SELLING': "В продаже",
            'STATUS_SOLD': "Продан",

            'REFERRAL_BUTTON': "- Реферальная система 🎁",
            'REFERRAL_MENU_MESSAGE': "**🎁︙Реферальная система**\n\n• Награда за каждого реферала: {reward}$\n• Всего приглашенных: {total_referred}\n• Общий заработок: {total_earned}$",
            'REFERRAL_LINK_MESSAGE': "**📎︙Ваша реферальная ссылка:**\n\n`{link}`\n\nПоделитесь этой ссылкой с друзьями и получайте {reward}$ за каждого друга, который присоединится!",
            'REFERRAL_STATS_MESSAGE': "**📊︙Статистика рефералов**\n\n• Всего приглашенных: {total_referred}\n• Общий заработок: {total_earned}$\n• Награда за каждого реферала: {reward}$",
            'NO_REFERRED_USERS': "⚠️︙Вы еще никого не пригласили",
        }
    }
}


class EnhancedLanguageManager:
    def __init__(self, db):
        self.db = db
        self.text_patterns = self._build_text_patterns()

    def _build_text_patterns(self):
        """بناء أنماط التعرف على النصوص من جميع اللغات"""
        patterns = {}

        # جمع جميع النصوص من جميع اللغات
        all_texts = set()
        for lang_data in LANGUAGES.values():
            for text in lang_data['messages'].values():
                if isinstance(text, str):
                    # إزالة المتغيرات مثل {} و {name} للتعرف على النمط الأساسي
                    clean_text = re.sub(r'{.*?}', '{}', text)
                    all_texts.add(clean_text)

        # إنشاء أنماط تعرف لكل نص
        for text in all_texts:
            if text.strip():  # تجاهل النصوص الفارغة
                patterns[text] = self._create_pattern(text)

        return patterns

    def _create_pattern(self, text):
        """إنشاء نمط تعرف للنص"""
        # تحويل النص إلى نمط تعرف مرن
        pattern = re.escape(text)
        pattern = pattern.replace(r'\{\}', r'\{.*?\}')  # جعل المتغيرات مرنة
        pattern = pattern.replace(r'\\ ', r'\s+')  # المسافات المرنة
        pattern = pattern.replace(r'\.', r'\.')  # النقاط
        return re.compile(pattern, re.IGNORECASE | re.DOTALL)

    def get_user_language(self, user_id):
        """الحصول على لغة المستخدم"""
        if self.db.exists(f"user_{user_id}"):
            user_data = self.db.get(f"user_{user_id}")
            return user_data.get('language', 'ar')
        return 'ar'

    def set_user_language(self, user_id, language):
        """تعيين لغة المستخدم"""
        if self.db.exists(f"user_{user_id}"):
            user_data = self.db.get(f"user_{user_id}")
            user_data['language'] = language
            self.db.set(f"user_{user_id}", user_data)
        else:
            self.db.set(f"user_{user_id}", {"coins": 0, "id": user_id, "language": language})

    def auto_translate_text(self, user_id, original_text):
        """ترجمة تلقائية لأي نص في البوت"""
        if not original_text or not isinstance(original_text, str):
            return original_text

        user_lang = self.get_user_language(user_id)

        # إذا كانت اللغة العربية، لا داعي للترجمة
        if user_lang == 'ar':
            return original_text

        # البحث عن النص في أنماط التعرف
        for pattern_text, pattern in self.text_patterns.items():
            if pattern.search(original_text):
                # البحث عن الترجمة المناسبة في اللغة المطلوبة
                translated = self._find_translation(pattern_text, user_lang)
                if translated:
                    # استبدال المتغيرات إذا وجدت
                    variables = self._extract_variables(original_text, pattern_text)
                    if variables:
                        try:
                            return translated.format(*variables)
                        except:
                            return translated
                    return translated

        # إذا لم يتم العثور على ترجمة، البحث في جميع النصوص يدوياً
        return self._manual_translate(original_text, user_lang)

    def _find_translation(self, pattern_text, target_lang):
        """البحث عن الترجمة للنمط المحدد"""
        if target_lang in LANGUAGES:
            for key, text in LANGUAGES[target_lang]['messages'].items():
                clean_text = re.sub(r'{.*?}', '{}', text)
                if clean_text == pattern_text:
                    return text

        # البحث في اللغات الأخرى
        for lang_code, lang_data in LANGUAGES.items():
            if lang_code != 'ar':  # تخطي العربية
                for key, text in lang_data['messages'].items():
                    clean_text = re.sub(r'{.*?}', '{}', text)
                    if clean_text == pattern_text:
                        # إذا كانت اللغة المطلوبة غير موجودة، نستخدم الإنجليزية
                        if target_lang in LANGUAGES and key in LANGUAGES[target_lang]['messages']:
                            return LANGUAGES[target_lang]['messages'][key]
                        elif key in LANGUAGES['en']['messages']:
                            return LANGUAGES['en']['messages'][key]

        return None

    def _extract_variables(self, original_text, pattern_text):
        """استخراج المتغيرات من النص الأصلي"""
        # إنشاء نمط استخراج المتغيرات
        pattern_parts = pattern_text.split('{}')
        if len(pattern_parts) <= 1:
            return []

        # استخراج المتغيرات
        variables = []
        current_text = original_text

        for i, part in enumerate(pattern_parts[:-1]):
            if part in current_text:
                start_idx = current_text.find(part) + len(part)
                if i < len(pattern_parts) - 1:
                    next_part = pattern_parts[i + 1]
                    if next_part in current_text[start_idx:]:
                        end_idx = current_text.find(next_part, start_idx)
                        variable = current_text[start_idx:end_idx]
                        variables.append(variable)
                        current_text = current_text[end_idx:]

        return variables

    def _manual_translate(self, text, target_lang):
        """ترجمة يدوية للنصوص غير المعروفة"""
        # قاموس للكلمات الشائعة
        common_words = {
            'ar': {'نعم': 'نعم', 'لا': 'لا', 'موافق': 'موافق', 'إلغاء': 'إلغاء', 'رجوع': 'رجوع', 'تم': 'تم',
                   'خطأ': 'خطأ', 'نجاح': 'نجاح'},
            'en': {'نعم': 'Yes', 'لا': 'No', 'موافق': 'OK', 'إلغاء': 'Cancel', 'رجوع': 'Back', 'تم': 'Done',
                   'خطأ': 'Error', 'نجاح': 'Success'},
            'fa': {'نعم': 'بله', 'لا': 'نه', 'موافق': 'تأیید', 'إلغاء': 'لغو', 'رجوع': 'بازگشت', 'تم': 'انجام شد',
                   'خطأ': 'خطا', 'نجاح': 'موفقیت'},
            'zh': {'نعم': '是', 'لا': '不', 'موافق': '确定', 'إلغاء': '取消', 'رجوع': '返回', 'تم': '完成',
                   'خطأ': '错误', 'نجاح': '成功'},
            'ru': {'نعم': 'Да', 'لا': 'Нет', 'موافق': 'ОК', 'إلغاء': 'Отмена', 'رجوع': 'Назад', 'تم': 'Готово',
                   'خطأ': 'Ошибка', 'نجاح': 'Успех'}
        }

        # ترجمة الكلمات الشائعة
        for word, translation in common_words.get(target_lang, common_words['en']).items():
            text = re.sub(rf'\b{word}\b', translation, text)
        return text

    def auto_translate_buttons(self, user_id, buttons):
        """ترجمة تلقائية للأزرار"""
        user_lang = self.get_user_language(user_id)

        if user_lang == 'ar':
            return buttons

        translated_buttons = []

        for button_row in buttons:
            translated_row = []
            for button in button_row:
                if hasattr(button, 'text') and hasattr(button, 'data'):
                    translated_text = self.auto_translate_text(user_id, button.text)
                    translated_row.append(Button.inline(translated_text, button.data))
                else:
                    translated_row.append(button)
            translated_buttons.append(translated_row)

        return translated_buttons

    def get_message(self, user_id, key, *args, **kwargs):
        """الحصول على رسالة باللغة المناسبة مع دعم المتغيرات المسماة وغير المسماة"""
        lang = self.get_user_language(user_id)
        message_text = ""

        if lang in LANGUAGES and key in LANGUAGES[lang]['messages']:
            message_text = LANGUAGES[lang]['messages'][key]
        else:
            if key in LANGUAGES['ar']['messages']:
                message_text = LANGUAGES['ar']['messages'][key]
            else:
                message_text = f"رسالة غير معروفة: {key}"

        # تم إضافة **kwargs ودعمها في .format()
        if args or kwargs:
            try:
                return message_text.format(*args, **kwargs)
            except Exception as e:
                print(f"⚠️ Error formatting message {key}: {e}")
                return message_text
        else:
            return message_text
    def get_settings_buttons(self, user_id):
        """الحصول على أزرار قائمة الإعدادات"""
        buttons = [
            [Button.inline(self.get_message(user_id, 'LANGUAGE_BUTTON'), data="change_language")],
            [Button.inline(self.get_message(user_id, 'CURRENCY_BUTTON'), data="change_currency")],
            [Button.inline(self.get_message(user_id, 'BACK_BUTTON'), data="main")]
        ]
        return buttons

    def get_main_buttons(self, user_id):
        """توزيع الأقسام على أزرار منفصلة ومنظمة في القائمة الرئيسية"""
        # تعريف الأزرار مباشرة دون دوال داخلية
        buttons = [
            # السطر الأول: 1 (أرقام عادية)
            [Button.inline("📞 شراء رقم", data="buy_cat_normal")],

            # السطر الثاني: 1 (إنشاء قديم)
            [Button.inline("⏳ حسابات انشاء قديمه", data="buy_cat_old_creation")],

            # السطر الثالث: 2 (مزيفة + احتيالية)
            [
                Button.inline("🤖 أرقام مزيف", data="buy_cat_fake"),
                Button.inline("⚠️ أرقام احتيالي", data="buy_cat_fraud")
            ],

            # السطر الرابع: 1 (كود الخصم)
            [Button.inline("🎟️ كود خصم", data="apply_coupon")],

            # السطر الخامس: 2 (شحن الرصيد + تحويل الرصيد)
            [
                Button.url(self.get_message(user_id, 'RECHARGE_BUTTON'), "https://t.me/QQ2iBOT"),
                Button.inline(self.get_message(user_id, 'TRANSFER_BUTTON'), data="transfer")
            ],

            # السطر السادس: 2 (نظام الإحالة + الإعدادات)
            [
                Button.inline(self.get_message(user_id, 'REFERRAL_BUTTON'), data="referral_system"),
                Button.inline(self.get_message(user_id, 'SETTINGS_MENU_BUTTON'), data="settings_menu")
            ],

            # السطر الأخير: 2 (الدعم الفني + القوانين)
            [
                Button.inline(self.get_message(user_id, 'SUPPORT_BUTTON'), data="support"),
                Button.inline(self.get_message(user_id, 'RULES_BUTTON'), data="liscgh")
            ]
        ]
        return buttons
    def smart_translate(self, user_id, obj):
        """دالة ذكية تترجم أي كائن (نص، أزرار، إلخ)"""
        if isinstance(obj, str):
            return self.auto_translate_text(user_id, obj)
        elif isinstance(obj, list):
            # إذا كان قائمة أزرار
            if obj and isinstance(obj[0], list):
                return self.auto_translate_buttons(user_id, obj)
            else:
                return [self.smart_translate(user_id, item) for item in obj]
        elif hasattr(obj, 'text') and hasattr(obj, 'data'):
            # إذا كان زر
            translated_text = self.auto_translate_text(user_id, obj.text)
            return Button.inline(translated_text, obj.data)
        else:
            return obj

    def detect_and_translate(self, text, user_id):
        """دالة للتوافق مع الكود القديم - تستخدم الترجمة الذكية"""
        return self.auto_translate_text(user_id, text)


# للتوافق مع الكود القديم
def setup_language_manager(db):
    return EnhancedLanguageManager(db)