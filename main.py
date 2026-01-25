import telebot
import base64
import json
import io

# ضع توكن بوتك هنا
TOKEN = '8367506658:AAFJVj903YeBPWGyCfVlUQcLPbnEDO5wV8Q'
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(func=lambda m: True)
def create_dark_file(message):
    url = message.text.strip()
    
    # التأكد أن الرابط يخص جوجل كلاود
    if "cloudshell.dev" in url:
        # تنظيف الرابط لاستخراج الدومين فقط
        # مثلاً نحول https://8080-cs...dev/ إلى 8080-cs...dev
        clean_domain = url.replace("https://", "").replace("http://", "").split('/')[0].split('?')[0]
        
        # بناء هيكل ملف Dark Tunnel
        config = {
            "type": "VLESS",
            "name": "🚀 سيرفر نت مجاني | @Alikhalafm",
            "vlessTunnelConfig": {
                "v2rayConfig": {
                    "host": "www.google.com",
                    "port": 443,
                    "uuid": "aaaa1111-bbbb-4ccc-8ddd-eeeeffff0000", # الـ UUID اللي استخدمناه
                    "serverNameIndication": "www.google.com",
                    "wsPath": "/",
                    "wsHeaderHost": clean_domain
                },
                "injectConfig": {
                    "enabled": True,
                    "mode": "PROXY",
                    "proxyHost": "157.240.9.39", # بروكسي فيسبوك لتخطى الحجب
                    "payload": f"CONNECT [host]:[port] HTTP/1.1\r\nHost: {clean_domain}\r\nConnection: Upgrade\r\n\r\n"
                }
            }
        }
        
        # تحويل الإعدادات إلى صيغة Dark Tunnel (Base64)
        json_str = json.dumps(config)
        encoded_config = base64.b64encode(json_str.encode()).decode()
        final_result = f"darktunnel://{encoded_config}"
        
        # إرسال النتيجة كنص وكملف محمل
        file_io = io.BytesIO(final_result.encode())
        file_io.name = "Alikhalafm_Net.dark"
        
        bot.reply_to(message, "✅ تم إنشاء ملفك بنجاح!")
        bot.send_document(message.chat.id, file_io, caption=f"👤 الحقوق: @Alikhalafm\n🔗 الدومين: {clean_domain}")
        bot.send_message(message.chat.id, f"📦 كود النسخ المباشر:\n\n`{final_result}`", parse_mode="Markdown")
    else:
        bot.reply_to(message, "⚠️ أرسل لي رابط Cloud Shell الصحيح (ينتهي بـ .dev)")

print("البوت يعمل الآن...")
bot.polling()