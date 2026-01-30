import logging
import base64
import json
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- الإعدادات الشخصية ---
BOT_TOKEN = "8290590965:AAGhdoPmd2L-VvXzpWmWKzxfpslpFZlyXeg" 
MY_ID = "@Alikhalafm"

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"📥 أرسل لي أي ملف .dark وسأقوم بتغيير جميع الحقوق لاسمك {MY_ID} فوراً!")

async def process_dark_logic(content):
    # إزالة البادئة وفك التشفير
    raw_encoded = content.replace("darktunnel://", "")
    decoded_json = json.loads(base64.b64decode(raw_encoded).decode())

    # --- تبديل الحقوق في كل مكان داخل الملف --- 
    decoded_json["name"] = f"VIP BY {MY_ID}" # تغيير الاسم الظاهر
    
    if "vlessTunnelConfig" in decoded_json:
        conf = decoded_json["vlessTunnelConfig"]["v2rayConfig"]
        conf["wsPath"] = f"/Telegram/{MY_ID}" # تغيير مسار التليجرام
        
        inject = decoded_json["vlessTunnelConfig"]["injectConfig"]
        # تغيير الحقوق داخل البايلود (Payload) 
        inject["payload"] = f"CONNECT [host]:[port] HTTP/1.1[crlf]X-Developer: {MY_ID}[crlf][crlf]"

    # إعادة التشفير
    new_encoded = base64.b64encode(json.dumps(decoded_json).encode()).decode()
    return f"darktunnel://{new_encoded}"

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    doc = update.message.document
    if not doc.file_name.endswith(".dark"):
        await update.message.reply_text("❌ يرجى إرسال ملف ينتهي بامتداد .dark")
        return

    status = await update.message.reply_text("🔄 جاري سحب الملف وتغيير الحقوق...")
    
    # تحميل الملف
    file = await context.bot.get_file(doc.file_id)
    file_path = "temp_file.dark"
    await file.download_to_drive(file_path)

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # معالجة الملف وتغيير الحقوق
        new_dark_content = await process_dark_logic(content)

        # حفظ الملف الجديد
        new_file_name = f"Updated_{MY_ID}.dark"
        with open(new_file_name, "w", encoding="utf-8") as f:
            f.write(new_dark_content)

        # إرسال الملف المعدل
        with open(new_file_name, "rb") as f:
            await update.message.reply_document(
                document=f,
                filename=new_file_name,
                caption=f"✅ تم تغيير حقوق الملف بنجاح!\n\n👤 الحقوق الجديدة: {MY_ID}"
            )
        
        os.remove(file_path)
        os.remove(new_file_name)
        await status.delete()

    except Exception as e:
        await update.message.reply_text(f"⚠️ حدث خطأ: تأكد أن الملف غير تالف.")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    print("البوت يعمل الآن... بانتظار الملفات.")
    app.run_polling()

if __name__ == "__main__":
    main()
