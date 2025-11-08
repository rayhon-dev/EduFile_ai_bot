import re

def mask_math_expressions(text: str):
    """
    Matematik ifodalarni tarjima jarayonida o‘zgarmasligi uchun masklaydi.
    Quyidagilarni aniqlaydi:
      ✅ LaTeX formulalar ($...$, \[...\], \(...\))
      ✅ Matritsalar ([[...]])
      ✅ Determinant (det(A))
      ✅ Transpoz (A^T, Bᵀ)
      ✅ Tenglamalar (A = B, x = 2y + 3)
      ✅ Arifmetik ifodalar (2+2, 3*4, 5-1, 2x + 3y)
      ✅ Maxsus matematik belgilar (π, √, ∑, ∫, ≤, ≥, ≈, ≠, ∆, ±, ∞, ∂)
      ✅ Indeks/yuqori belgilar (x₁, y²)
    """

    # Kengaytirilgan regex patternlar
    pattern = re.compile(
        r'('
        r'\$[^$]+\$|'                  # $...$
        r'\\\[.*?\\\]|'                # \[...\]
        r'\\\(.*?\\\)|'                # \(...\)
        r'\[\[[^\]]+\]\]|'             # [[...]]
        r'det\s*\([^)]+\)|'            # det(...)
        r'[A-Za-zА-Яа-я]\s*\^\s*T|'    # A^T, B^T
        r'[A-Za-zА-Яа-я]\s*[₀-₉⁰-⁹]|'  # indeks (x₁)
        r'[A-Za-zА-Яа-я]\s*\^\s*\d+|'  # yuqori belgi (y^2)
        r'\b\d+(\.\d+)?\s*[\+\-\*/=]\s*\d+(\.\d+)?\b|'  # 2 + 3, 5*4
        r'[A-Za-zА-Яа-я]+\s*=\s*[A-Za-zА-Яа-я0-9\+\-\*/\^\(\)]+|'  # x = 2y + 1
        r'[π∞√∑∫≤≥≈≠∆±∂∇∫∬∭≡∝∪∩∈∉⊂⊃⊆⊇]|'  # matematik belgilar
        r'[A-Za-zА-Яа-я]+\s*\([A-Za-zА-Яа-я0-9,\+\-\*/\s]+\)|'  # f(x), sin(x), cos(2θ)
        r'\b\d+(\.\d+)?\s*[xX*/^+-]\s*\d+(\.\d+)?\b'            # 2.5 * 3
        r')',
        flags=re.DOTALL
    )

    placeholders = {}

    def replacer(match):
        key = f"[MATH_EXPR_{len(placeholders)}]"
        placeholders[key] = match.group(0)
        return key

    masked = pattern.sub(replacer, text)
    return masked, placeholders


def unmask_math_expressions(text: str, placeholders: dict):
    """
    Masklangan matematik ifodalarni asl holiga qaytaradi.
    Tartib bilan joylashtirish uchun maxsus iteratsiya ishlatiladi.
    """
    # Oxiridagi ']' belgisi olib tashlanadi, shunda int conversion xato bermaydi
    sorted_placeholders = sorted(
        placeholders.items(),
        key=lambda x: int(x[0].split('_')[-1].rstrip(']'))
    )
    for key, expr in sorted_placeholders:
        text = text.replace(key, expr)
    return text



def safe_translate_math(text: str, translate_func):
    """
    Matematik ifodalarni tarjimadan himoya qiladi.
    1️⃣ Masklaydi
    2️⃣ Tarjima qiladi (faqat matn)
    3️⃣ Asl formulalarni tiklaydi
    """
    masked_text, placeholders = mask_math_expressions(text)
    translated_masked = translate_func(masked_text)
    final_text = unmask_math_expressions(translated_masked, placeholders)
    return final_text


