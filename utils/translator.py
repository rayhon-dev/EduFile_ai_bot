import google.generativeai as genai
import os
from utils.math_detector import mask_math_expressions, unmask_math_expressions

# API kalitni sozlash
genai.configure(api_key=os.getenv("GEMINI_API_KEY") or "YOUR_API_KEY_HERE")

def translate_text_preserving_math(content: str) -> str:
    # Free versiyada ishlaydigan model
    model = genai.GenerativeModel("models/gemini-2.5-flash")

    # Matematik qismlarni vaqtincha masklash
    masked, placeholders = mask_math_expressions(content)

    # Tarjima uchun prompt
    prompt = f"""
    Translate the following text to English.
    Do NOT translate or modify any placeholders like [MATH_EXPR_0].
    Just translate the sentences around them.

    Input:
    {masked}
    """

    # So‘rov yuborish
    response = model.generate_content(prompt)

    # To‘g‘ri matnni olish
    if response.candidates:
        translated = response.candidates[0].content.parts[0].text.strip()
    else:
        translated = ""

    # Matematik ifodalarni tiklash
    translated = unmask_math_expressions(translated, placeholders)

    return translated