import os
from PyPDF2 import PdfReader
from docx import Document

def read_file_content(file_path: str) -> str:
    """
    .txt, .md, .pdf, va .docx fayllarni o‘qiydi va matn sifatida qaytaradi.
    """
    try:
        # 1️⃣ Oddiy matnli fayllar
        if file_path.endswith((".txt", ".md")):
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()

        # 2️⃣ PDF fayllar
        elif file_path.endswith(".pdf"):
            text = ""
            reader = PdfReader(file_path)
            for page in reader.pages:
                text += page.extract_text() or ""
            return text.strip()

        # 3️⃣ Word fayllar (.docx)
        elif file_path.endswith(".docx"):
            doc = Document(file_path)
            text = "\n".join([p.text for p in doc.paragraphs])
            return text.strip()

        # 4️⃣ Noma’lum format
        else:
            return "❗ Fayl turi qo‘llab-quvvatlanmaydi. Faqat .txt, .md, .pdf, va .docx fayllar ishlaydi."

    except Exception as e:
        print(f"Error reading file: {e}")
        return None
