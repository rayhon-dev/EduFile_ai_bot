import re

def mask_math_expressions(text: str):
    """
    Matematika ifodalarini [MATH_EXPR_n] bilan almashtiradi,
    keyin tarjimadan keyin tiklash uchun.
    """
    math_patterns = re.findall(r'(\d+[\+\-\*/=]\d+|[A-Za-z]*\d+[A-Za-z]*|\d+\s?[xX]|x\s?[=<>]\s?\d+)', text)
    masked = text
    placeholders = {}

    for i, expr in enumerate(math_patterns):
        placeholder = f"[MATH_EXPR_{i}]"
        placeholders[placeholder] = expr
        masked = masked.replace(expr, placeholder, 1)

    return masked, placeholders


def unmask_math_expressions(translated_text: str, placeholders: dict):
    """
    Tarjimadan keyin [MATH_EXPR_n] ni asl matematik ifodalar bilan almashtiradi.
    """
    for placeholder, expr in placeholders.items():
        translated_text = translated_text.replace(placeholder, expr)
    return translated_text
