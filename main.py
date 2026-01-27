import telebot
import base64
import json
import io
import random
import string
import re
from telebot import types
from urllib.parse import unquote

# --- الإعدادات ---
TOKEN = '8367506658:AAFJVj903YeBPWGyCfVlUQcLPbnEDO5wV8Q'
ADMIN_ID = 1049669606 
CHANNELS = ["@teamofghost"]
bot = telebot.TeleBot(TOKEN)
MY_RIGHTS = "Alikhalafm"

authorized_users = set()
user_steps = {}

# --- الدوال الأساسية ---

def extract_host_smartly(text):
    text = unquote(text)
    # النمط الجديد يدعم gnas و tqsw وأي منطقة أخرى تظهر مستقبلاً
    match = re.search(r'([a-zA-Z0-9\-]+\.ql\-[a-z0-9\-]+\.cloudshell\.dev)', text)
    if match:
        return match.group(1).strip().lower()
    return None

def check_sub(user_id):
    for channel in CHANNELS:
        try:
            status = bot.get_chat_member(channel, user_id).status
            if status in ['left', 'kicked']: return False
        except: continue 
    return True

def generate_stealth(length=6000):
    return ''.join(random.choices(string.ascii_letters + string.digits + "!@#$%^&*", k=length))

# --- معالجة الرسائل ---

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if not check_sub(user_id):
        markup = types.InlineKeyboardMarkup()
        for ch in CHANNELS:
            markup.add(types.InlineKeyboardButton("اشتراك 🔗", url=f"https://t.me/{ch.replace('@','')}"))
        markup.add(types.InlineKeyboardButton("تم الاشتراك ✅", callback_data="verify_sub"))
        bot.send_message(user_id, f"⚠️ اشترك أولاً في قناة {MY_RIGHTS}:", reply_markup=markup)
        return

    if user_id not in authorized_users and user_id != ADMIN_ID:
        bot.send_message(ADMIN_ID, f"🔔 طلب تفعيل: `{user_id}`", 
                         reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("تفعيل ✅", callback_data=f"auth_{user_id}")))
        bot.send_message(user_id, "⏳ انتظر موافقة الأدمن...")
        return
    bot.send_message(user_id, "🚀 أرسل رابط المختبر (gnas أو tqsw) وسأقوم بصنع الملف!")

@bot.message_handler(func=lambda m: True)
def handle_messages(message):
    user_id = message.from_user.id
    if user_id in authorized_users or user_id == ADMIN_ID:
        clean_host = extract_host_smartly(message.text)
        if clean_host:
            user_steps[message.chat.id] = {'url': clean_host}
            markup = types.InlineKeyboardMarkup()
            # إضافة خيار آسيا + أثير هنا
            markup.add(types.InlineKeyboardButton("آسيا سيل 🟡", callback_data="net_asia"),
                       types.InlineKeyboardButton("أثير 🔴", callback_data="net_atheer"))
            markup.add(types.InlineKeyboardButton("آسيا + أثير 🟢", callback_data="net_mixed"))
            bot.reply_to(message, f"🎯 تم استخراج الهوست:\n`{clean_host}`\n\nاختر الشبكة:", parse_mode="Markdown", reply_markup=markup)
        else:
            bot.reply_to(message, "❌ لم يتم العثور على رابط صالح.")

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    if call.data == "verify_sub": start(call.message)
    elif call.data.startswith("auth_"):
        uid = int(call.data.split("_")[1]); authorized_users.add(uid)
        bot.send_message(uid, "✅ تم تفعيلك!"); bot.edit_message_text(f"✅ تم تفعيل {uid}", ADMIN_ID, call.message.message_id)
    
    elif call.data.startswith("net_"):
        net = call.data.split("_")[1]
        user_steps[chat_id]['net'] = net
        # سيسأل عن الباقة لكل الأنواع بما فيها mixed
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("باقة سوشيال ✅", callback_data=f"mode_social_{net}"),
                   types.InlineKeyboardButton("بدون باقة ❌", callback_data=f"mode_direct_{net}"))
        bot.edit_message_text(f"🛠️ اختر الإعداد لـ {net.upper()}:", chat_id, call.message.message_id, reply_markup=markup)

    elif call.data.startswith("mode_"):
        _, mode, net = call.data.split("_")
        create_file(chat_id, mode, net)

def create_file(chat_id, mode, net):
    data = user_steps.get(chat_id)
    host = data['url']
    sni = "www.google.com" # SNI افتراضي مستقر
    
    # تحديد البروكسي: إذا كان "mixed" نستخدم بروكسي آسيا كونه يدعم الأثنين غالباً
    proxy = "104.18.24.243" 
    if net == "atheer": proxy = "157.240.9.39"
    
    config = {
        "type": "VLESS",
        "name": f"🛡️ VVIP-{MY_RIGHTS}-{net.upper()}-{mode.upper()}",
        "isLocked": True,
        "vlessTunnelConfig": {
            "v2rayConfig": {
                "host": sni, "port": 443,
                "uuid": "aaaa1111-bbbb-4ccc-8ddd-eeeeffff0000",
                "serverNameIndication": sni,
                "wsPath": "/", "wsHeaderHost": host
            },
            "injectConfig": {
                "enabled": True if mode == "social" else False,
                "mode": "PROXY",
                "proxyHost": proxy,
                "payload": "CONNECT [host]:[port] HTTP/1.1[crlf]Host: [host][crlf]Connection: keep-alive[crlf][crlf]"
            }
        },
        "ultra_stealth": generate_stealth(6000),
        "owner": MY_RIGHTS
    }
    
    encoded = base64.b64encode(json.dumps(config).encode()).decode()
    with io.BytesIO(f"darktunnel://{encoded}".encode()) as f:
        f.name = f"VVIP_{MY_RIGHTS}_{net}_{mode}.dark"
        bot.send_document(chat_id, f, caption=f"✅ تم التجهيز بنجاح!\n🌐 الشبكة: {net.upper()}\n🔓 النوع: {mode.upper()}")

bot.infinity_polling()
