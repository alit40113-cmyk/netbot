import telebot
import base64
import json
from telebot import types

# --- الإعدادات الأساسية ---
TOKEN = '8367506658:AAFJVj903YeBPWGyCfVlUQcLPbnEDO5wV8Q'
ADMIN_ID = 1049669606  # !!! ضع أيديك هنا
CHANNELS = ["@teamofghost"] # ضع قنواتك هنا
bot = telebot.TeleBot(TOKEN)

# تخزين مؤقت للمستخدمين (يتم تصفيره عند إعادة تشغيل الكود)
authorized_users = set()
user_steps = {}

def check_sub(user_id):
    """التحقق من الاشتراك في القنوات"""
    for channel in CHANNELS:
        try:
            status = bot.get_chat_member(channel, user_id).status
            if status in ['left', 'kicked']:
                return False
        except:
            continue 
    return True

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    
    # 1. فحص الاشتراك الإجباري
    if not check_sub(user_id):
        markup = types.InlineKeyboardMarkup()
        for ch in CHANNELS:
            markup.add(types.InlineKeyboardButton("اشترك هنا 🔗", url=f"https://t.me/{ch.replace('@','')}"))
        markup.add(types.InlineKeyboardButton("تم الاشتراك ✅", callback_data="verify_sub"))
        bot.send_message(user_id, "⚠️ عذراً، يجب أن تشترك في القناة أولاً لاستخدام البوت:", reply_markup=markup)
        return

    # 2. فحص موافقة المالك
    if user_id not in authorized_users and user_id != ADMIN_ID:
        bot.send_message(ADMIN_ID, f"🔔 طلب تفعيل جديد:\n👤 {message.from_user.first_name}\n🆔 `{user_id}`", 
                         reply_markup=types.InlineKeyboardMarkup().add(
                             types.InlineKeyboardButton("تفعيل الحساب ✅", callback_data=f"auth_{user_id}")))
        bot.send_message(user_id, "⏳ تم إرسال طلبك للمالك. يرجى الانتظار حتى يتم تفعيل حسابك...")
        return

    bot.send_message(user_id, "🚀 أهلاً بك في بوت VVIP. أرسل الآن رابط Cloud Shell الخاص بك.")

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == "verify_sub":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        start(call.message)
    
    elif call.data.startswith("auth_"):
        user_to_auth = int(call.data.split("_")[1])
        authorized_users.add(user_to_auth)
        bot.answer_callback_query(call.id, "تم تفعيل المستخدم!")
        bot.send_message(user_to_auth, "🎉 مبروك! تم تفعيل حسابك من قبل المالك. يمكنك الآن استخدام البوت.")
        bot.edit_message_text(f"✅ تم تفعيل {user_to_auth}", ADMIN_ID, call.message.message_id)

    elif call.data.startswith("net_"):
        net_type = call.data.split("_")[1]
        user_steps[call.message.chat.id]['net'] = net_type
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("سوشيال (بايلود)", callback_data="mode_social"),
                   types.InlineKeyboardButton("بدون باقة (مباشر)", callback_data="mode_direct"))
        bot.edit_message_text("🛠️ اختر نوع الباقة (الثغرة):", call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif call.data.startswith("mode_"):
        mode = call.data.split("_")[1]
        chat_id = call.message.chat.id
        create_file(chat_id, mode)

def create_file(chat_id, mode):
    data = user_steps.get(chat_id)
    if not data: return
    
    # استخراج الهوست من الرابط
    raw_url = data['url']
    clean_host = raw_url.replace("https://", "").split("/")[0]
    
    # [cite_start]إعدادات V2Ray (VLESS) بناءً على الملف الذي أرسلته [cite: 1]
    v2ray_config = {
        "host": clean_host,
        "port": 443,
        "uuid": "aaaa1111-bbbb-4ccc-8ddd-eeeeffff0000", # UUID موحد
        "serverNameIndication": "www.google.com",
        "wsPath": "/Telegram/@AM2_D3",
        "wsHeaderHost": clean_host
    }
    
    # إعدادات الحقن (Injection)
    inject_config = {
        "enabled": True if mode == "social" else False,
        "mode": "PROXY",
        [cite_start]"proxyHost": "157.240.9.39", # بروكسي فيسبوك [cite: 1]
        "payload": "CONNECT [host]:[port] HTTP/1.1[crlf]Host: [host][crlf]Connection: keep-alive[crlf][crlf]"
    }
    
    final_json = {
        "type": "VLESS",
        "name": f"VVIP-{data['net'].upper()}",
        "vlessTunnelConfig": {
            "v2rayConfig": v2ray_config,
            "injectConfig": inject_config
        },
        "isLocked": True # قفل الملف لحماية سيرفرك
    }
    
    # تحويل إلى صيغة Dark Tunnel
    json_str = json.dumps(final_json)
    encoded = base64.b64encode(json_str.encode()).decode()
    dark_config = f"darktunnel://{encoded}"
    
    # إرسال النتيجة
    bot.send_message(chat_id, f"✅ تم صنع ملفك بنجاح!\n\n`{dark_config}`", parse_mode="Markdown")

@bot.message_handler(func=lambda m: "cloudshell.dev" in m.text)
def handle_link(message):
    if message.from_user.id not in authorized_users and message.from_user.id != ADMIN_ID:
        return
    
    user_steps[message.chat.id] = {'url': message.text.strip()}
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("آسيا سيل", callback_data="net_asia"),
               types.InlineKeyboardButton("زين العراق", callback_data="net_zain"))
    bot.reply_to(message, "🌐 اختر شبكتك الآن:", reply_markup=markup)

bot.polling()
