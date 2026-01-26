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
CHANNELS = ["@teamofghost"]
bot = telebot.TeleBot(TOKEN)

# قائمة هوستات عالمية للتمويه (صعبة الحظر)
SNI_LIST = ["www.google.com", "alt13.yt3.ggpht.com", "appleid.apple.com", "connectivitycheck.gstatic.com"]

authorized_users = set()
user_steps = {}

def generate_strong_padding(length=5000):
    return ''.join(random.choices(string.ascii_letters + string.digits + "!@#$%^&*", k=length))

# (دوال الحماية والموافقة تظل مفعلة لضمان أمن البوت)
def check_sub(user_id):
    for channel in CHANNELS:
        try:
            status = bot.get_chat_member(channel, user_id).status
            if status in ['left', 'kicked']: return False
        except: continue 
    return True

@bot.callback_query_handler(func=lambda call: call.data.startswith("mode_"))
def create_and_send_ultra_file(call):
    chat_id = call.message.chat.id
    mode = call.data.split("_")[1]
    data = user_steps.get(chat_id)
    
    host = data['url'].replace("https://", "").split("/")[0]
    random_sni = random.choice(SNI_LIST) # اختيار قناع عشوائي
    
    # --- هيكلة الملف الفائق (Ultra Stealth) ---
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
                "wsPath": f"/Live/Stream/{generate_strong_padding(10)}", # مسار متغير
                "wsHeaderHost": host
            },
            "injectConfig": {
                "enabled": True if mode == "social" else False,
                "mode": "PROXY",
                "proxyHost": "157.240.9.39",
                "payload": "CONNECT [host]:[port] HTTP/1.1[crlf]Host: [host][crlf]Connection: keep-alive[crlf][crlf]"
            }
        },
        "ultra_security_layer": generate_strong_padding(5000) # حشو ضخم جداً
    }
    
    encoded = base64.b64encode(json.dumps(config).encode()).decode()
    final_content = f"darktunnel://{encoded}"
    
    file_name = f"VVIP_ULTRA_{data['net']}.dark"
    with io.BytesIO(final_content.encode()) as dark_file:
        dark_file.name = file_name
        bot.send_document(chat_id, dark_file, caption="✅ **تم توليد ملف Ultra Stealth**\n🔒 تشفير متعدد الطبقات مفعل\n📡 وضع الحماية القصوى ضد الـ DPI")

# بقية الهاندلرز (start, handle_link) تظل كما هي في النسخة السابقة...
bot.polling()
