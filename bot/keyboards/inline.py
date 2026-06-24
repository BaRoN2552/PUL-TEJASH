from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_currency_keyboard() -> InlineKeyboardMarkup:
    """Keyboard for selecting default currency."""
    buttons = [
        [InlineKeyboardButton(text="So'm (UZS)", callback_data="set_currency_UZS"),
         InlineKeyboardButton(text="Dollar (USD)", callback_data="set_currency_USD")],
        [InlineKeyboardButton(text="Yevro (EUR)", callback_data="set_currency_EUR"),
         InlineKeyboardButton(text="Rubl (RUB)", callback_data="set_currency_RUB")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_reports_keyboard() -> InlineKeyboardMarkup:
    """Keyboard for triggering reports."""
    buttons = [
        [InlineKeyboardButton(text="📊 Bugungi hisobot", callback_data="report_daily"),
         InlineKeyboardButton(text="📅 Haftalik hisobot", callback_data="report_weekly")],
        [InlineKeyboardButton(text="📆 Oylik hisobot", callback_data="report_monthly")],
        [InlineKeyboardButton(text="🤖 AI maslahat", callback_data="report_ai"),
         InlineKeyboardButton(text="📤 Excel Eksport", callback_data="report_excel")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_confirm_keyboard(action: str) -> InlineKeyboardMarkup:
    """Generic confirmation keyboard."""
    buttons = [
        [InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"confirm_{action}"),
         InlineKeyboardButton(text="❌ Bekor qilish", callback_data=f"cancel_{action}")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_account_type_keyboard() -> InlineKeyboardMarkup:
    """Keyboard for account types."""
    buttons = [
        [InlineKeyboardButton(text="💵 Naqd", callback_data="acc_type_cash"),
         InlineKeyboardButton(text="💳 Karta", callback_data="acc_type_card")],
        [InlineKeyboardButton(text="📱 Elektron Hamyon", callback_data="acc_type_wallet")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
