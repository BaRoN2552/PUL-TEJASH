from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery

from bot.services.finance_service import finance_service
from bot.keyboards.inline import get_currency_keyboard
from bot.keyboards.reply import get_main_menu

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    full_name = message.from_user.full_name

    # Registers user and creates a default 'Naqd' account
    await finance_service.get_or_create_user(user_id, username, full_name)
    
    greeting = (
        f"Salom, {full_name or 'Foydalanuvchi'}! 💰\n"
        f"Shaxsiy moliyaviy yordamchi botiga xush kelibsiz.\n\n"
        f"Bu bot orqali kirim/chiqimlaringizni hisoblab, "
        f"byudjet va maqsadlar qo'yishingiz hamda moliyaviy "
        f"ahvolingiz haqida chiroyli grafikli hisobotlar olishingiz mumkin.\n\n"
        f"Davom etish uchun asosiy valyutangizni tanlang:"
    )
    await message.answer(greeting, reply_markup=get_currency_keyboard())

@router.callback_query(F.data.startswith("set_currency_"))
async def callback_set_currency(callback: CallbackQuery):
    currency = callback.data.split("_")[2]
    user_id = callback.from_user.id
    
    await finance_service.update_user(user_id, currency=currency)
    await callback.answer(f"Asosiy valyuta {currency} qilib belgilandi.")
    
    await callback.message.answer(
        "Ajoyib! Asosiy menyu yuklandi. Quyidagi tugmalar orqali botdan foydalanishingiz mumkin👇",
        reply_markup=get_main_menu()
    )
    await callback.message.delete()

@router.message(Command("yordam"))
async def cmd_help(message: Message):
    help_text = (
        "💡 **MOLIYAVIY BOT BUYRUQLARI**\n\n"
        "🟢 **Asosiy amallar:**\n"
        "• `/start` - Botni qayta ishga tushirish\n"
        "• `/balans` - Hisoblar balansini ko'rish\n"
        "• `/kirim` yoki 'Kirim' tugmasi - Kirim yozish\n"
        "• `/chiqim` yoki 'Chiqim' tugmasi - Chiqim yozish\n"
        "• `/t [miqdor] [tavsif]` - Tezkor chiqim yozish (Masalan: `/t 15000 non`)\n\n"
        "🔵 **Hisobotlar:**\n"
        "• `/kun` yoki 'Hisobotlar' -> 'Bugun'\n"
        "• `/hafta` - Haftalik hisobot\n"
        "• `/oy` - Oylik hisobot\n"
        "• `/eksport` - Tranzaksiyalarni Excelga yuklash\n"
        "• `/maslahat` - AI moliyaviy tavsiyalari\n\n"
        "🟡 **Boshqaruv:**\n"
        "• `/byudjet` - Byudjetni sozlash\n"
        "• `/maqsad` - Moliyaviy maqsadlar\n"
        "• `/qarzlar` - Qarz oldi-berdisi\n"
        "• `/hisoblar` - Hisoblar boshqaruvi\n"
    )
    await message.answer(help_text)
