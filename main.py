import telebot
import base64
import json
from telebot import types

# --- الإعدادات الأساسية ---
TOKEN = '8367506658:AAFJVj903YeBPWGyCfVlUQcLPbnEDO5wV8Q'
ADMIN_ID = 1049669606  # ضع أيديك هنا (أرقام فقط)
CHANNELS = ["@teamofghost"] # ضع معرف قناتك هنا
bot = telebot.TeleBot(TOKEN)

authorized_users = set()
user_steps = {}

def check_sub(user_id):
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
    if not check_sub(user_id):
        markup = types.InlineKeyboardMarkup()
        for ch in CHANNELS:
            markup.add(types.InlineKeyboardButton("اشترك هنا 🔗", url=f"https://t.me/{ch.replace('@','')}"))
        markup.add(types.InlineKeyboardButton("تم الاشتراك ✅", callback_data="verify_sub"))
        bot.send_message(user_id, "⚠️ اشترك بالقناة أولاً:", reply_markup=markup)
        return

    if user_id not in authorized_users and user_id != ADMIN_ID:
        bot.send_message(ADMIN_ID, f"🔔 طلب تفعيل:\n👤 {message.from_user.first_name}\n🆔 `{user_id}`", 
                         reply_markup=types.InlineKeyboardMarkup().add(
                             types.InlineKeyboardButton("تفعيل ✅", callback_data=f"auth_{user_id}")))
        bot.send_message(user_id, "⏳ بانتظار تفعيل المالك...")
        return
    bot.send_message(user_id, "🚀 أرسل رابط Cloud Shell.")

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == "verify_sub":
        start(call.message)
    elif call.data.startswith("auth_"):
        uid = int(call.data.split("_")[1])
        authorized_users.add(uid)
        bot.send_message(uid, "✅ تم تفعيل حسابك!")
        bot.edit_message_text(f"✅ تم تفعيل {uid}", ADMIN_ID, call.message.message_id)
    elif call.data.startswith("net_"):
        user_steps[call.message.chat.id]['net'] = call.data.split("_")[1]
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("سوشيال", callback_data="mode_social"),
                   types.InlineKeyboardButton("مباشر", callback_data="mode_direct"))
        bot.edit_message_text("🛠️ نوع الباقة:", call.message.chat.id, call.message.message_id, reply_markup=markup)
    elif call.data.startswith("mode_"):
        create_file(call.message.chat.id, call.data.split("_")[1])

def create_file(chat_id, mode):
    data = user_steps.get(chat_id)
    host = data['url'].replace("https://", "").split("/")[0]
    
    # بناء الإعدادات 
    config = {
        "type": "VLESS",
        "name": f"VVIP-{data['net']}",
        "vlessTunnelConfig": {
            "v2rayConfig": {
                "host": host, "port": 443, "uuid": "aaaa1111-bbbb-4ccc-8ddd-eeeeffff0000",
                "serverNameIndication": "www.google.com", "wsPath": "/Telegram/@AM2_D3", "wsHeaderHost": host
            },
            "injectConfig": {
                "enabled": True if mode == "social" else False,
                "mode": "PROXY",
                "proxyHost": "157.240.9.39", # بروكسي فيسبوك من المصدر 
                "payload": "CONNECT [host]:[port] HTTP/1.1[crlf]Host: [host][crlf]Connection: keep-alive[crlf][crlf]"
            }
        },
        "isLocked": True
    }
    
    encoded = base64.b64encode(json.dumps(config).encode()).decode()
    bot.send_message(chat_id, f"✅ ملفك جاهز:\n\n`darktunnel://{encoded}`")

@bot.message_handler(func=lambda m: "cloudshell.dev" in m.text)
def handle_link(message):
    if message.from_user.id in authorized_users or message.from_user.id == ADMIN_ID:
        user_steps[message.chat.id] = {'url': message.text.strip()}
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("آسيا", callback_data="net_asia"),
                   types.InlineKeyboardButton("زين", callback_data="net_zain"))
        bot.reply_to(message, "🌐 اختر الشبكة:", reply_markup=markup)

bot.polling()
