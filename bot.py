import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import google.generativeai as genai
from utils.file_parser import read_file_content
from utils.translator import translate_text_preserving_math

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_KEY)


# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📘 Salom! Fayl yuboring — men uni ingliz tiliga tarjima qilib qaytaraman.")


# Faylni qabul qilish va tarjima
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.document.get_file()
    filename = update.message.document.file_name

    os.makedirs("downloads", exist_ok=True)
    file_path = f"downloads/{filename}"
    await file.download_to_drive(file_path)

    # Faylni o‘qish
    content = read_file_content(file_path)
    if not content:
        await update.message.reply_text("❌ Faylni o‘qib bo‘lmadi.")
        return

    # Tarjima qilish
    translated_text = translate_text_preserving_math(content)

    # Tarjima qilingan faylni saqlash va yuborish
    output_path = f"downloads/translated_{filename}"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(translated_text)

    await update.message.reply_document(document=open(output_path, "rb"))

    os.remove(file_path)
    os.remove(output_path)


# Botni ishga tushirish
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.Document.ALL, handle_file))
app.run_polling()
