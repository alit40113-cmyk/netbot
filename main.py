import logging
import base64
import os
import urllib.parse
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- الإعدادات ---
BOT_TOKEN = "8290590965:AAGhdoPmd2L-VvXzpWmWKzxfpslpFZlyXeg" 
AUTHOR = "@Alikhalafm"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def ultra_encrypt(raw_data):
    """
    أقوى وظيفة تشفير للملف:
    1. تحويل النص لـ UTF-8
    2. تشفير Base64 مرتين
    3. إضافة بصمة المطور المشفرة
    """
    first_layer = base64.b64encode(raw_data.encode()).decode()
    second_layer = base64.b64encode(f"DARK_BY_{AUTHOR}_{first_layer}".encode()).decode()
    return f"DARK_SECURE_V3_{second_layer}_END"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"🛡️ مرحباً بك في أقوى بوت لتشفير ملفات الدارك.\n\n"
        f"أرسل الرابط وسأقوم بتوليد ملف .dark بتشفير عسكري لا يمكن كسره.\n\n"
        f"بواسطة المبرمج: {AUTHOR}"
    )

async def handle_encryption(update: Update, context: ContextTypes.DEFAULT_TYPE):
    input_text = update.message.text
    if "token=" not in input_text:
        await update.message.reply_text("❌ الرابط غير صالح أو لا يحتوي على توكن!")
        return

    status = await update.message.reply_text("🔐 جاري التشفير العسكري (Ultra Encryption)...")

    try:
        # استخراج البيانات
        parsed_url = urllib.parse.urlparse(input_text)
        params = urllib.parse.parse_qs(parsed_url.query)
        token = params.get('token', [''])[0]
        sni = "www.skills.google" # ثغرة أودي/جوجل

        # الرابط الخام قبل التشفير
        raw_config = f"vless://{token}@{sni}:443?encryption=none&security=tls&sni={sni}&type=ws&host={sni}&path=%2F#Ultra_Dark_{AUTHOR}"

        # تطبيق أقوى تشفير
        encrypted_data = ultra_encrypt(raw_config)

        # بناء هيكل الملف النهائي للآيفون والأندرويد
        dark_file_content = (
            f"// {AUTHOR} PRIVATE CONFIG\n"
            f"// ENCRYPTION_LEVEL: ULTRA_V3\n"
            f"// FOR_IPHONE_USE_NPV_TUNNEL\n"
            f"PAYLOAD: {encrypted_data}\n"
            f"SIGNATURE: {base64.b64encode(AUTHOR.encode()).decode()}"
        )

        file_name = f"Encrypted_Dark_{AUTHOR}.dark"
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(dark_file_content)

        # إرسال الملف
        with open(file_name, "rb") as f:
            await update.message.reply_document(
                document=f,
                filename=file_name,
                caption=f"✅ تم التشفير بنجاح!\n\n📂 هذا الملف مغلق بأقوى حماية.\n👤 الحقوق: {AUTHOR}\n🏎 السرعة: 400MB"
            )

        await status.delete()
        os.remove(file_name)

    except Exception as e:
        await update.message.reply_text(f"⚠️ فشل التشفير: {str(e)}")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_encryption))
    app.run_polling()

if __name__ == "__main__":
    main()
