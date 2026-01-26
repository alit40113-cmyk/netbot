import telebot
import base64
import json
import io
import random
import string
from telebot import types

# --- الإعدادات ---
TOKEN = '8367506658:AAFJVj903YeBPWGyCfVlUQcLPbnEDO5wV8Q'
ADMIN_ID = 1049669606 
CHANNELS = ["@teamofghost"] # ضع يوزر قناتك الحقيقي هنا
bot = telebot.TeleBot(TOKEN)

MY_RIGHTS = "Alikhalafm"
SNI_LIST = ["www.google.com", "appleid.apple.com", "connectivitycheck.gstatic.com"]

authorized_users = set()
user_steps = {}

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
    # 1. فحص الاشتراك
    if not check_sub(user_id):
        markup = types.InlineKeyboardMarkup()
        for ch in CHANNELS:
            markup.add(types.InlineKeyboardButton("اشترك هنا 🔗", url=f"https://t.me/{ch.replace('@','')}"))
        markup.add(types.InlineKeyboardButton("تم الاشتراك ✅", callback_data="verify_sub"))
        bot.send_message(user_id, f"⚠️ مرحباً بك.. اشترك بقناة {MY_RIGHTS} أولاً:", reply_markup=markup)
        return

    # 2. فحص الموافقة
    if user_id not in authorized_users and user_id != ADMIN_ID:
        bot.send_message(ADMIN_ID, f"🔔 طلب تفعيل جديد:\n👤 {message.from_user.first_name}\n🆔 `{user_id}`", 
                         reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("تفعيل ✅", callback_data=f"auth_{user_id}")))
        bot.send_message(user_id, f"⏳ طلبك بانتظar موافقة المالك {MY_RIGHTS}...")
        return
    bot.send_message(user_id, "🚀 أرسل رابط Cloud Shell الآن:")

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    if call.data == "verify_sub": start(call.message)
    elif call.data.startswith("auth_"):
        uid = int(call.data.split("_")[1])
        authorized_users.add(uid)
        bot.send_message(uid, "✅ تم تفعيلك بنجاح! يمكنك إرسال الروابط الآن.")
        bot.edit_message_text(f"✅ تم تفعيل {uid}", ADMIN_ID, call.message.message_id)
    
    # اختيار نوع الباقة بعد اختيار الشبكة
    elif call.data.startswith("net_"):
        net = call.data.split("_")[1]
        user_steps[chat_id]['net'] = net
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("باقة سوشيال ✅", callback_data=f"mode_social_{net}"),
                   types.InlineKeyboardButton("بدون باقة ❌", callback_data=f"mode_direct_{net}"))
        bot.edit_message_text(f"🛠️ خيارات {net.upper()}:\nاختر نوع الاتصال المطلوبة:", chat_id, call.message.message_id, reply_markup=markup)
    
    # المعالجة النهائية وصنع الملف
    elif call.data.startswith("mode_"):
        _, mode, net = call.data.split("_")
        create_ultra_file(chat_id, mode, net)

@bot.message_handler(func=lambda m: "cloudshell.dev" in m.text)
def handle_link(message):
    if message.from_user.id in authorized_users or message.from_user.id == ADMIN_ID:
        user_steps[message.chat.id] = {'url': message.text.split('?')[0].strip()}
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("آسيا سيل 🟡", callback_data="net_asia"))
        markup.add(types.InlineKeyboardButton("أثير 🔴", callback_data="net_atheer"))
        markup.add(types.InlineKeyboardButton("آسيا + أثير 🟢", callback_data="net_mixed"))
        bot.reply_to(message, "🌐 اختر الشبكة:", reply_markup=markup)

def create_ultra_file(chat_id, mode, net):
    data = user_steps.get(chat_id)
    host = data['url'].replace("https://", "").strip()
    sni = random.choice(SNI_LIST)
    
    # إعدادات البروكسي الذكية
    proxy = "104.18.24.243" 
    if "atheer" in net: proxy = "157.240.9.39"
    
    config = {
        "type": "VLESS",
        "name": f"🛡️ VVIP-{MY_RIGHTS}-{net.upper()}",
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
    file_label = "SOCIAL" if mode == "social" else "DIRECT"
    file_name = f"VVIP_{MY_RIGHTS}_{net}_{file_label}.dark"
    
    with io.BytesIO(f"darktunnel://{encoded}".encode()) as f:
        f.name = file_name
        bot.send_document(chat_id, f, caption=f"✅ **تم تجهيز ملف {MY_RIGHTS}**\n📡 الشبكة: {net.upper()}\n⚙️ النظام: {file_label}\n🔓 المسار: / (Fixed)")

bot.infinity_polling()
