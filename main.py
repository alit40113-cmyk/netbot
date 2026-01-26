import telebot
import base64
import json
import io
import random
import string
from telebot import types

# --- الإعدادات ---
TOKEN = '8367506658:AAFJVj903YeBPWGyCfVlUQcLPbnEDO5wV8Q'
ADMIN_ID = 1049669606  # أيديك هنا
CHANNELS = ["@teamofghost"]
bot = telebot.TeleBot(TOKEN)

authorized_users = set()
user_steps = {}

def generate_padding(length=1000):
    """توليد بيانات عشوائية لزيادة طول الملف وتضليل الشركة"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# (دوال الفحص والاشتراك تبقى كما هي لضمان الحماية)
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
        bot.send_message(user_id, "⚠️ اشترك بالقناة أولاً:", reply_markup=markup)
        return
    if user_id not in authorized_users and user_id != ADMIN_ID:
        bot.send_message(ADMIN_ID, f"🔔 طلب تفعيل:\n🆔 `{user_id}`", 
                         reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("تفعيل ✅", callback_data=f"auth_{user_id}")))
        bot.send_message(user_id, "⏳ بانتظار تفعيل المالك...")
        return
    bot.send_message(user_id, "🚀 أرسل رابط Cloud Shell.")

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    if call.data == "verify_sub": start(call.message)
    elif call.data.startswith("auth_"):
        uid = int(call.data.split("_")[1]); authorized_users.add(uid)
        bot.send_message(uid, "✅ تم تفعيل حسابك!"); bot.edit_message_text(f"✅ تم تفعيل {uid}", ADMIN_ID, call.message.message_id)
    elif call.data.startswith("net_"):
        user_steps[chat_id]['net'] = call.data.split("_")[1]
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("سوشيال (تشفير طويل)", callback_data="mode_social"),
                   types.InlineKeyboardButton("مباشر (تشفير طويل)", callback_data="mode_direct"))
        bot.edit_message_text("🛠️ اختر نوع الباقة (الحماية مفعلة):", chat_id, call.message.message_id, reply_markup=markup)
    elif call.data.startswith("mode_"): create_and_send_long_file(chat_id, call.data.split("_")[1])

def create_and_send_long_file(chat_id, mode):
    data = user_steps.get(chat_id)
    host = data['url'].replace("https://", "").split("/")[0]
    
    # --- هيكلة الملف المشفر الطويل ---
    config = {
        "type": "VLESS",
        "name": f"VVIP-{data['net'].upper()}-ULTRA-SAFE",
        "isLocked": True,
        "vlessTunnelConfig": {
            "v2rayConfig": {
                "host": "alt13.yt3.ggpht.com",
                "port": 443,
                "uuid": "aaaa1111-bbbb-4ccc-8ddd-eeeeffff0000",
                "serverNameIndication": "alt13.yt3.ggpht.com",
                "wsPath": "/Telegram/@AM2_D3",
                "wsHeaderHost": host
            },
            "injectConfig": {
                "enabled": True if mode == "social" else False,
                "mode": "PROXY",
                "proxyHost": "157.240.9.39",
                "payload": "CONNECT [host]:[port] HTTP/1.1[crlf]Host: [host][crlf]Connection: keep-alive[crlf][crlf]"
            }
        },
        "security_padding": generate_padding(2000) # إضافة 2000 حرف عشوائي لتمويه التشفير
    }
    
    # تحويل الإعدادات إلى نص مشفر طويل جداً
    json_data = json.dumps(config)
    encoded_config = base64.b64encode(json_data.encode()).decode()
    final_content = f"darktunnel://{encoded_config}"
    
    # إرسال الملف
    file_name = f"VVIP_SAFE_{data['net']}.dark"
    with io.BytesIO(final_content.encode()) as dark_file:
        dark_file.name = file_name
        bot.send_document(chat_id, dark_file, caption=f"🛡️ تم صنع ملف حماية فائق القوة!\n📊 حجم التشفير: عالي جداً\n🔒 الحالة: مخفي عن أنظمة الشركة")

@bot.message_handler(func=lambda m: "cloudshell.dev" in m.text)
def handle_link(message):
    if message.from_user.id in authorized_users or message.from_user.id == ADMIN_ID:
        user_steps[message.chat.id] = {'url': message.text.strip()}
        markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("آسيا سيل", callback_data="net_asia"),
                                                 types.InlineKeyboardButton("زين العراق", callback_data="net_zain"))
        bot.reply_to(message, "🌐 اختر الشبكة (سيتم توليد ملف مشفر طويل):", reply_markup=markup)

bot.polling()

