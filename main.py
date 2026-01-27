import telebot
import base64
import json
import io
import random
import string
import re
from telebot import types
from urllib.parse import unquote

# --- الإعدادات (تأكد من وضع التوكن الخاص بك) ---
TOKEN = '8367506658:AAFJVj903YeBPWGyCfVlUQcLPbnEDO5wV8Q'
ADMIN_ID = 1049669606 
CHANNELS = ["@Alikhalafm_channel"] # يوزر قناتك
bot = telebot.TeleBot(TOKEN)

MY_RIGHTS = "Alikhalafm"
SNI_LIST = ["www.google.com", "appleid.apple.com", "connectivitycheck.gstatic.com"]

authorized_users = set()
user_steps = {}

# دالة ذكية لاستخراج الهوست الصافي من أي نص أو رابط طويل
def extract_host_smartly(text):
    text = unquote(text) # فك ترميز الرابط إذا كان معقداً
    # البحث عن نمط الـ cloudshell داخل أي نص
    match = re.search(r'([a-zA-Z0-9\-]+\.ql\-europe\-west4\-tqsw\.cloudshell\.dev)', text)
    if match:
        return match.group(1).strip().strip("/")
    return None

def generate_stealth(length=6000):
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
        bot.send_message(user_id, f"⚠️ اشترك بقناة المطور {MY_RIGHTS} أولاً:", reply_markup=markup)
        return

    if user_id not in authorized_users and user_id != ADMIN_ID:
        bot.send_message(ADMIN_ID, f"🔔 طلب تفعيل جديد:\n👤 {message.from_user.first_name}\n🆔 `{user_id}`", 
                         reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("تفعيل ✅", callback_data=f"auth_{user_id}")))
        bot.send_message(user_id, f"⏳ طلبك بانتظار موافقة {MY_RIGHTS}...")
        return
    bot.send_message(user_id, "🚀 أرسل رابط المختبر أو رابط الـ Shell الآن.\nسأقوم باستخراج الهوست وصنع الملف تلقائياً!")

@bot.message_handler(func=lambda m: True)
def handle_messages(message):
    user_id = message.from_user.id
    if user_id in authorized_users or user_id == ADMIN_ID:
        clean_host = extract_host_smartly(message.text)
        
        if clean_host:
            user_steps[message.chat.id] = {'url': clean_host}
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("آسيا سيل 🟡", callback_data="net_asia"),
                       types.InlineKeyboardButton("أثير 🔴", callback_data="net_atheer"),
                       types.InlineKeyboardButton("آسيا + أثير 🟢", callback_data="net_mixed"))
            bot.reply_to(message, f"🎯 تم استخراج الهوست الصافي:\n`{clean_host}`\n\nاختر الشبكة الآن:", parse_mode="Markdown", reply_markup=markup)
        else:
            bot.reply_to(message, "❌ لم أجد رابط Cloud Shell في النص المرسل. تأكد من فتح المختبر أولاً.")

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    if call.data == "verify_sub": start(call.message)
    elif call.data.startswith("auth_"):
        uid = int(call.data.split("_")[1])
        authorized_users.add(uid)
        bot.send_message(uid, "✅ تم تفعيلك! يمكنك الآن إرسال الروابط.")
        bot.edit_message_text(f"✅ تم تفعيل {uid}", ADMIN_ID, call.message.message_id)
    elif call.data.startswith("net_"):
        net = call.data.split("_")[1]
        user_steps[chat_id]['net'] = net
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("باقة سوشيال ✅", callback_data=f"mode_social_{net}"),
                   types.InlineKeyboardButton("بدون باقة ❌", callback_data=f"mode_direct_{net}"))
        bot.edit_message_text(f"🛠️ اختر النوع لشبكة {net.upper()}:", chat_id, call.message.message_id, reply_markup=markup)
    elif call.data.startswith("mode_"):
        _, mode, net = call.data.split("_")
        create_final_file(chat_id, mode, net)

def create_final_file(chat_id, mode, net):
    data = user_steps.get(chat_id)
    host = data['url']
    sni = random.choice(SNI_LIST)
    
    config = {
        "type": "VLESS",
        "name": f"🛡️ VVIP-{MY_RIGHTS}-{net.upper()}",
        "isLocked": True,
        "vlessTunnelConfig": {
            "v2rayConfig": {
                "host": sni, "port": 443,
                "uuid": "aaaa1111-bbbb-4ccc-8ddd-eeeeffff0000",
                "serverNameIndication": sni,
                "wsPath": "/", "wsHeaderHost": host # الهوست هنا نظيف تماماً
            },
            "injectConfig": {
                "enabled": True if mode == "social" else False,
                "mode": "PROXY",
                "proxyHost": "157.240.9.39" if "atheer" in net else "104.18.24.243",
                "payload": "CONNECT [host]:[port] HTTP/1.1[crlf]Host: [host][crlf]Connection: keep-alive[crlf][crlf]"
            }
        },
        "ultra_stealth": generate_stealth(6000),
        "owner": MY_RIGHTS
    }
    
    encoded = base64.b64encode(json.dumps(config).encode()).decode()
    file_name = f"VVIP_{MY_RIGHTS}_{net}_{mode}.dark"
    with io.BytesIO(f"darktunnel://{encoded}".encode()) as f:
        f.name = file_name
        bot.send_document(chat_id, f, caption=f"✅ **تم تجهيز الملف بنجاح!**\n👤 المطور: {MY_RIGHTS}\n🔗 الهوست: `{host}`\n🔓 النظام: {mode.upper()}")

bot.infinity_polling()
