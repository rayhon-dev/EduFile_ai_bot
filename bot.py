import os
import re
import asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from docx import Document
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

from utils.file_parser import read_file_content
from utils.translator import translate_text_preserving_math

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN muhit o‘zgaruvchisi aniqlanmadi!")

# Ruxsat etilgan fayl turlari va limit (MB)
ALLOWED_EXTENSIONS = {".txt", ".md", ".pdf", ".docx"}
MAX_FILE_SIZE_MB = 10


def secure_filename(filename: str) -> str:
    """Fayl nomini xavfsiz holatga keltirish."""
    return re.sub(r'[^a-zA-Z0-9_\.\-]', '_', filename)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📘 Salom! Menga .txt, .docx, .pdf, yoki .md fayl yuboring — men uni ingliz tiliga tarjima qilib qaytaraman.\n"
        f"Maksimal fayl hajmi: {MAX_FILE_SIZE_MB} MB."
    )


async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    document = update.message.document
    if not document:
        await update.message.reply_text("❌ Hech qanday fayl topilmadi.")
        return

    filename = secure_filename(document.file_name)
    ext = os.path.splitext(filename)[1].lower()

    if ext not in ALLOWED_EXTENSIONS:
        await update.message.reply_text(
            f"❗ Fayl formati qo‘llab-quvvatlanmaydi: {ext}. Faqat {', '.join(ALLOWED_EXTENSIONS)} ruxsat etilgan."
        )
        return

    file_size_mb = document.file_size / (1024 * 1024)
    if file_size_mb > MAX_FILE_SIZE_MB:
        await update.message.reply_text(
            f"❗ Fayl hajmi katta: {file_size_mb:.2f} MB. Maksimal ruxsat etilgan: {MAX_FILE_SIZE_MB} MB."
        )
        return

    os.makedirs("downloads", exist_ok=True)
    file_path = f"downloads/{filename}"
    output_path = None

    try:
        # Faylni yuklab olish
        telegram_file = await document.get_file()
        await telegram_file.download_to_drive(file_path)
        await update.message.reply_text("📂 Fayl yuklandi. Tarjima jarayoni boshlandi...")

        # Matnni o‘qish
        content = await asyncio.to_thread(read_file_content, file_path)
        if not content or not content.strip():
            await update.message.reply_text("❌ Fayl bo‘sh yoki o‘qib bo‘lmadi.")
            return

        # Bot "typing" holatini ko‘rsatish
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

        # Tarjima qilish (async safe)
        translated_text = await asyncio.to_thread(translate_text_preserving_math, content)
        if not translated_text:
            await update.message.reply_text("⚠️ Tarjima amalga oshirilmadi.")
            return

        base_name = os.path.splitext(filename)[0]
        output_path = f"downloads/{base_name}_translated{ext}"

        # Natijani faylga yozish
        if ext in {".txt", ".md"}:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(translated_text)

        elif ext == ".docx":
            doc = Document()
            for paragraph in translated_text.splitlines():
                doc.add_paragraph(paragraph)
            doc.save(output_path)

        elif ext == ".pdf":
            c = canvas.Canvas(output_path, pagesize=letter)
            y = 750
            line_height = 14
            text_obj = c.beginText(50, y)
            text_obj.setFont("Helvetica", 11)
            for line in translated_text.splitlines():
                if y < 50:
                    c.drawText(text_obj)
                    c.showPage()
                    y = 750
                    text_obj = c.beginText(50, y)
                    text_obj.setFont("Helvetica", 11)
                text_obj.textLine(line)
                y -= line_height
            c.drawText(text_obj)
            c.save()

        else:
            await update.message.reply_text("❗ Fayl formati qo‘llab-quvvatlanmaydi.")
            return

        # Tarjima qilingan faylni yuborish
        with open(output_path, "rb") as out_file:
            await update.message.reply_document(
                document=out_file,
                filename=os.path.basename(output_path),
                caption=f"✅ Tarjima tugadi! ({ext} formatda)"
            )

    except Exception as e:
        await update.message.reply_text(f"❌ Xatolik yuz berdi: {str(e)}")

    finally:
        # Fayllarni tozalash
        try:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
            if output_path and os.path.exists(output_path):
                os.remove(output_path)
        except Exception:
            pass


if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_file))
    print("🤖 Bot ishga tushdi...")
    app.run_polling()
