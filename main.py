import telebot
import base64
import json
import io
import random
import string
from telebot import types

# --- الإعدادات ---
TOKEN = '8367506658:AAFJVj903YeBPWGyCfVlUQcLPbnEDO5wV8Q'
ADMIN_ID = 1049669606  # !!! استبدل هذا برقم أيديك الحقيقي
CHANNELS = ["@YourChannel1"]
bot = telebot.TeleBot(TOKEN)

SNI_LIST = ["www.google.com", "alt13.yt3.ggpht.com", "appleid.apple.com", "connectivitycheck.gstatic.com"]
authorized_users = set()
user_steps = {}

def generate_strong_padding(length=5000):
    return ''.join(random.choices(string.ascii_letters + string.digits + "!@#$%^&*", k=length))

def check_sub(user_id):
    for channel in CHANNELS:
        try:
            status = bot.get_chat_member(channel, user_id).status
            if status in ['left', 'kicked']: return False
        except: continue 
    return True

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if not check_sub(user_id):
        markup = types.InlineKeyboardMarkup()
        for ch in CHANNELS:
            markup.add(types.InlineKeyboardButton("اشترك هنا 🔗", url=f"https://t.me/{ch.replace('@','')}"))
        markup.add(types.InlineKeyboardButton("تم الاشتراك ✅", callback_data="verify_sub"))
        bot.send_message(user_id, "⚠️ اشترك بالقناة أولاً لتفعيل البوت:", reply_markup=markup)
        return

    if user_id not in authorized_users and user_id != ADMIN_ID:
        try:
            bot.send_message(ADMIN_ID, f"🔔 طلب تفعيل جديد:\n👤 {message.from_user.first_name}\n🆔 `{user_id}`", 
                             reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("تفعيل الحساب ✅", callback_data=f"auth_{user_id}")))
            bot.send_message(user_id, "⏳ تم إرسال طلبك للمالك.. انتظر التفعيل.")
        except:
            bot.send_message(user_id, "❌ خطأ: الآدمن لم يقم بتشغيل البوت بعد.")
        return
    bot.send_message(user_id, "🚀 أهلاً بك في نظام Ultra Stealth. أرسل رابط Cloud Shell الآن.")

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    if call.data == "verify_sub":
        start(call.message)
    elif call.data.startswith("auth_"):
        uid = int(call.data.split("_")[1])
        authorized_users.add(uid)
        bot.send_message(uid, "🎉 مبروك! تم تفعيل حسابك من قبل المالك.")
        bot.edit_message_text(f"✅ تم تفعيل {uid}", ADMIN_ID, call.message.message_id)
    elif call.data.startswith("net_"):
        user_steps[chat_id]['net'] = call.data.split("_")[1]
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("سوشيال (بايلود)", callback_data="mode_social"),
                   types.InlineKeyboardButton("بدون باقة (مباشر)", callback_data="mode_direct"))
        bot.edit_message_text("🛠️ اختر نوع الباقة (الحماية Ultra مفعلة):", chat_id, call.message.message_id, reply_markup=markup)
    elif call.data.startswith("mode_"):
        create_and_send_ultra_file(chat_id, call.data.split("_")[1])

def create_and_send_ultra_file(chat_id, mode):
    data = user_steps.get(chat_id)
    host = data['url'].replace("https://", "").split("/")[0]
    random_sni = random.choice(SNI_LIST)
    
    config = {
        "type": "VLESS",
        "name": f"🛡️ VVIP-ULTRA-{random.randint(100,999)}",
        "isLocked": True,
        "vlessTunnelConfig": {
            "v2rayConfig": {
                "host": random_sni,
                "port": 443,
                "uuid": "aaaa1111-bbbb-4ccc-8ddd-eeeeffff0000",
                "serverNameIndication": random_sni,
                "wsPath": f"/Live/Stream/{generate_strong_padding(10)}",
                "wsHeaderHost": host
            },
            "injectConfig": {
                "enabled": True if mode == "social" else False,
                "mode": "PROXY",
                "proxyHost": "157.240.9.39",
                "payload": "CONNECT [host]:[port] HTTP/1.1[crlf]Host: [host][crlf]Connection: keep-alive[crlf][crlf]"
            }
        },
        "ultra_security_layer": generate_strong_padding(5000)
    }
    
    encoded = base64.b64encode(json.dumps(config).encode()).decode()
    file_name = f"VVIP_ULTRA_{data['net']}.dark"
    with io.BytesIO(f"darktunnel://{encoded}".encode()) as dark_file:
        dark_file.name = file_name
        bot.send_document(chat_id, dark_file, caption="✅ **تم توليد ملف Ultra Stealth بنجاح!**\n💎 صالح لمدة ساعتين (عمر السيرفر).")

@bot.message_handler(func=lambda m: "cloudshell.dev" in m.text)
def handle_link(message):
    if message.from_user.id in authorized_users or message.from_user.id == ADMIN_ID:
        user_steps[message.chat.id] = {'url': message.text.strip()}
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("آسيا سيل", callback_data="net_asia"),
                   types.InlineKeyboardButton("زين العراق", callback_data="net_zain"))
        bot.reply_to(message, "🌐 اختر الشبكة لتوليد ملف مشفر:", reply_markup=markup)

print("✅ Bot is Online and Waiting for messages...")
bot.polling(none_stop=True)

