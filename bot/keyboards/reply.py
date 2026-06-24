from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_menu() -> ReplyKeyboardMarkup:
    """Returns the persistent main menu keyboard."""
    kb = [
        [KeyboardButton(text="💰 Kirim"), KeyboardButton(text="💸 Chiqim")],
        [KeyboardButton(text="💵 Balans"), KeyboardButton(text="📊 Hisobotlar")],
        [KeyboardButton(text="📅 Byudjet"), KeyboardButton(text="🎯 Maqsadlar")],
        [KeyboardButton(text="🤝 Qarzlar"), KeyboardButton(text="⚙️ Sozlamalar")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="Kerakli bo'limni tanlang...")
