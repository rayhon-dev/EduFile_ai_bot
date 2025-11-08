import os
import google.generativeai as genai
from utils.math_detector import safe_translate_math


def configure_genai():
    from dotenv import load_dotenv
    load_dotenv()  # Bu yerda ham chaqirish mumkin
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY muhit o'zgaruvchisi topilmadi!")
    genai.configure(api_key=api_key)

configure_genai()


def translate_text_preserving_math(content: str, source_lang="uz", target_lang="en") -> str:
    """
    Matematika, formulalar va matritsalarni o‘zgartirmasdan tarjima qiladi.
    Default: Uzbek → English
    """

    model = genai.GenerativeModel("models/gemini-2.5-flash")

    def gemini_translate(text):
        prompt = f"""
You are a professional translator.

Translate this text from {source_lang.upper()} to {target_lang.upper()}.

IMPORTANT:
- Do NOT translate or modify anything inside placeholders like [MATH_EXPR_0], <FORMULA_0>, etc.
- Preserve all mathematical expressions, symbols, and formatting exactly.
- Only translate the regular text outside placeholders.

Text to translate:
{text}
"""
        try:
            response = model.generate_content(prompt)
            if not response or not response.candidates:
                return text

            candidate = response.candidates[0]
            if not candidate.content or not candidate.content.parts:
                return text

            translated = "".join(
                getattr(part, "text", "") for part in candidate.content.parts
            ).strip()

            return translated or text

        except Exception as e:
            print(f"[Translation Error] {e}")
            return text

    return safe_translate_math(content, gemini_translate)
