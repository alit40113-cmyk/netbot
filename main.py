import telebot
import base64
import json
import io
from telebot import types

# ضع توكن بوتك هنا
TOKEN = '8367506658:AAFJVj903YeBPWGyCfVlUQcLPbnEDO5wV8Q'
bot = telebot.TeleBot(TOKEN)

# تخزين مؤقت للروابط المستلمة
user_links = {}

@bot.message_handler(func=lambda m: True)
def ask_network(message):
    url = message.text.strip()
    if "cloudshell.dev" in url:
        user_links[message.chat.id] = url
        
        # إنشاء أزرار الاختيار
        markup = types.InlineKeyboardMarkup()
        btn_asia = types.InlineKeyboardButton("Asiacell (آسيا)", callback_data="network_asia")
        btn_zain = types.InlineKeyboardButton("Zain (زين/أثير)", callback_data="network_zain")
        markup.add(btn_asia, btn_zain)
        
        bot.reply_to(message, "🌐 اختر الشبكة التي تريد تشغيل الملف عليها بدون باقة:", reply_markup=markup)
    else:
        bot.reply_to(message, "⚠️ أرسل لي رابط Cloud Shell الصحيح (ينتهي بـ .dev)")

@bot.callback_query_handler(func=lambda call: call.data.startswith("network_"))
def process_callback(call):
    chat_id = call.message.chat.id
    if chat_id not in user_links:
        bot.answer_callback_query(call.id, "❌ حدث خطأ، أرسل الرابط مرة أخرى.")
        return

    url = user_links[chat_id]
    clean_domain = url.replace("https://", "").replace("http://", "").split('/')[0].split('?')[0]
    
    # تحديد الهوست حسب الاختيار ليعمل بدون باقة
    if call.data == "network_asia":
        sni_host = "free.asiacell.com"
        proxy_ip = "157.240.9.39"  # بروكسي فيسبوك المعتاد لآسيا 
        net_name = "Asiacell 🥝"
    else:
        sni_host = "zain.com.iq"
        proxy_ip = "157.240.9.39" # يمكن استخدامه لزين أيضاً في بعض الثغرات [cite: 2]
        net_name = "Zain/Atheer 💎"

    # بناء هيكل ملف Dark Tunnel المطور
    config = {
        "type": "VLESS",
        "name": f"🚀 {net_name} | @Alikhalafm",
        "vlessTunnelConfig": {
            "v2rayConfig": {
                "host": sni_host,  # الهوست المجاني لتخطي الحجب
                "port": 443,
                "uuid": "aaaa1111-bbbb-4ccc-8ddd-eeeeffff0000", 
                "serverNameIndication": sni_host, # الـ SNI المجاني
                "wsPath": "/",
                "wsHeaderHost": clean_domain # الرابط الأصلي للسيرفر
            },
            "injectConfig": {
                "enabled": True,
                "mode": "PROXY",
                "proxyHost": proxy_ip,
                "payload": f"CONNECT [host]:[port] HTTP/1.1\r\nHost: {clean_domain}\r\nConnection: Upgrade\r\n\r\n"
            }
        }
    }

    # تحويل وتشفير الملف
    json_str = json.dumps(config)
    encoded_config = base64.b64encode(json_str.encode()).decode()
    final_result = f"darktunnel://{encoded_config}"

    file_io = io.BytesIO(final_result.encode())
    file_io.name = f"Alikhalafm_{call.data.split('_')[1]}.dark"

    bot.delete_message(chat_id, call.message.message_id)
    bot.send_document(chat_id, file_io, caption=f"✅ تم الإنشاء لشبكة: {net_name}\n🔗 السيرفر: {clean_domain}")
    bot.send_message(chat_id, f"📦 كود النسخ المباشر:\n\n`{final_result}`", parse_mode="Markdown")
    
    # مسح الرابط من الذاكرة
    del user_links[chat_id]

print("البوت مطور ويعمل الآن...")
bot.polling()
