import telebot
import base64
import json
import io
from telebot import types

# توكن البوت
TOKEN = '8367506658:AAFJVj903YeBPWGyCfVlUQcLPbnEDO5wV8Q'
bot = telebot.TeleBot(TOKEN)

# ذاكرة مؤقتة لتخزين بيانات المستخدم
user_data = {}

@bot.message_handler(func=lambda m: True)
def ask_network(message):
    url = message.text.strip()
    if "cloudshell.dev" in url:
        user_data[message.chat.id] = {'url': url}
        markup = types.InlineKeyboardMarkup()
        btn_asia = types.InlineKeyboardButton("Asiacell (آسيا)", callback_data="net_asia")
        btn_zain = types.InlineKeyboardButton("Zain (زين/أثير)", callback_data="net_zain")
        markup.add(btn_asia, btn_zain)
        bot.reply_to(message, "🌐 اختر الشبكة أولاً:", reply_markup=markup)
    else:
        bot.reply_to(message, "⚠️ أرسل رابط Cloud Shell الصحيح.")

@bot.callback_query_handler(func=lambda call: call.data.startswith("net_"))
def process_network(call):
    chat_id = call.message.chat.id
    user_data[chat_id]['network'] = call.data
    
    markup = types.InlineKeyboardMarkup()
    btn_yes = types.InlineKeyboardButton("نعم، عندي باقة ✅", callback_data="social_yes")
    btn_no = types.InlineKeyboardButton("لا، بدون باقة ❌", callback_data="social_no")
    markup.add(btn_yes, btn_no)
    
    bot.edit_message_text("❓ هل تملك باقة سوشيال (فيسبوك/واتساب)؟", chat_id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("social_"))
def process_final(call):
    chat_id = call.message.chat.id
    url = user_data[chat_id]['url']
    network = user_data[chat_id]['network']
    has_social = call.data == "social_yes"
    
    clean_domain = url.replace("https://", "").replace("http://", "").split('/')[0].split('?')[0]
    
    # تحديد الهوست بناءً على نوع الشبكة ووجود الباقة
    if "asia" in network:
        sni = "www.facebook.com" if has_social else "free.asiacell.com"
        net_label = "Asiacell 🥝"
    else:
        sni = "c.whatsapp.net" if has_social else "zain.com.iq"
        net_label = "Zain 💎"

    config = {
        "type": "VLESS",
        "name": f"🔐 {net_label} | {'Social' if has_social else 'No-Package'}",
        "vlessTunnelConfig": {
            "v2rayConfig": {
                "host": sni,
                "port": 443,
                "uuid": "aaaa1111-bbbb-4ccc-8ddd-eeeeffff0000", 
                "serverNameIndication": sni,
                "wsPath": "/",
                "wsHeaderHost": clean_domain
            },
            "injectConfig": {
                "enabled": True,
                "mode": "PROXY",
                "proxyHost": "157.240.9.39" if has_social else "", # ترك البروكسي فارغ في حالة بدون باقة ليعتمد على الـ SNI
                "payload": f"GET / HTTP/1.1\r\nHost: {clean_domain}\r\nConnection: Upgrade\r\nUpgrade: websocket\r\n\r\n"
            }
        },
        "isLocked": True
    }

    encoded = base64.b64encode(json.dumps(config).encode()).decode()
    final_result = f"darktunnel://{encoded}"
    
    file_io = io.BytesIO(final_result.encode())
    file_io.name = f"{net_label}_{'Social' if has_social else 'Free'}.dark"

    bot.delete_message(chat_id, call.message.message_id)
    bot.send_document(chat_id, file_io, caption=f"✅ تم تجهيز الملف!\n🌐 الشبكة: {net_label}\n💡 الحالة: {'باقة سوشيال' if has_social else 'بدون باقة'}")
    del user_data[chat_id]

print("البوت الذكي يعمل الآن...")
bot.polling()
