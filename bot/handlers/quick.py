import re
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy import select

from bot.database import async_session_maker
from bot.models.category import Category
from bot.services.finance_service import finance_service

router = Router()

def guess_category_name(desc: str, tx_type: str) -> str:
    """Guess the category based on description keywords."""
    desc = desc.lower()
    if tx_type == "expense":
        mapping = {
            "Oziq-ovqat": ["non", "sut", "go'sht", "bozor", "supermarket", "magazin", "kartoshka", "piyoz", "meva", "ovqat", "shirinlik"],
            "Transport": ["taksi", "benzin", "avtobus", "metro", "yo'l", "yol", "zapchast", "mashina", "yandex", "metan", "propan"],
            "Ijara": ["kvartira", "ijara", "uy", "arend", "depozit"],
            "Sog'liq": ["dori", "apteka", "doktor", "shifoxona", "klinika", "tish", "analiz", "shifokor"],
            "Ko'ngilochar": ["kino", "teatr", "konsert", "pubg", "o'yin", "oyun", "sayohat", "dam olish", "hordiq"],
            "Kafe": ["kafe", "choyxona", "osh", "kabob", "kofe", "coffee", "pits", "pizza", "burger", "shashlik", "choy", "restoran", "lavash"],
            "Kommunal": ["svet", "gaz", "suv", "musor", "internet", "wifi", "telefon", "tarif", "kommunal", "paynet"]
        }
        for cat, keywords in mapping.items():
            if any(k in desc for k in keywords):
                return cat
        return "Xarid"
    else:
        mapping = {
            "Maosh": ["maosh", "oylik", "salary", "karta", "avans", "kpi", "daromad"],
            "Sovg'a": ["sovg'a", "sovga", "gift", "mukofot", "bonus", "hadya"]
        }
        for cat, keywords in mapping.items():
            if any(k in desc for k in keywords):
                return cat
        return "Qo'shimcha daromad"

async def process_quick_transaction(message: Message, tx_type: str, args_text: str):
    """Processes shorthand transactions like /t 15000 taksi or /kirim 500000 oylik"""
    user_id = message.from_user.id
    
    # Pattern to match: [amount][optional currency] [description]
    # e.g., "50000 taksi" or "10 USD taksi"
    match = re.match(r"^(\d+(?:\.\d+)?)\s*([A-Z]{3})?\s+(.+)$", args_text.strip(), re.IGNORECASE)
    if not match:
        await message.answer(
            f"⚠️ Buyruq formati noto'g'ri.\n"
            f"To'g'ri namuna:\n"
            f"• `{message.text.split()[0]} 20000 taksi`\n"
            f"• `{message.text.split()[0]} 50 USD kiyim`"
        )
        return

    amount = float(match.group(1))
    currency = (match.group(2) or "UZS").upper()
    description = match.group(3).strip()

    # Determine category
    category_name = guess_category_name(description, tx_type)
    
    async with async_session_maker() as session:
        # Find category ID in DB
        res_cat = await session.execute(
            select(Category).where(Category.name == category_name, Category.type == tx_type)
        )
        category = res_cat.scalar_one_or_none()
        if not category:
            # Fallback to system default default Category
            res_cat_fallback = await session.execute(
                select(Category).where(Category.is_default == True, Category.type == tx_type)
            )
            category = res_cat_fallback.scalars().first()

        # Find user default account (e.g., first account)
        accounts = await finance_service.get_user_accounts(user_id)
        if not accounts:
            await message.answer("❌ Hisoblaringiz topilmadi. Avval `/start` orqali ro'yxatdan o'ting.")
            return
            
        account = accounts[0] # Usually the default "Naqd" account

        try:
            tx, budget_alert = await finance_service.create_transaction(
                user_id=user_id,
                account_id=account.id,
                category_id=category.id,
                tx_type=tx_type,
                amount=amount,
                currency=currency,
                description=description
            )
            
            sign = "+" if tx_type == "income" else "-"
            symbol = "💰" if tx_type == "income" else "💸"
            
            response = (
                f"{symbol} **Tezkor tranzaksiya saqlandi!**\n\n"
                f"💵 **Miqdor:** {sign}{amount:,.2f} {currency}\n"
                f"📌 **Kategoriya:** {category.icon} {category.name}\n"
                f"💳 **Hisob:** {account.icon} {account.name}\n"
                f"📝 **Tavsif:** {description}\n"
            )
            
            if budget_alert:
                if budget_alert["status"] == "exceeded":
                    response += (
                        f"\n🚨 **BYUDJET OSHIB KETDI!**\n"
                        f"Limit: {budget_alert['limit']:,.0f} so'm\n"
                        f"Sarflangan: {budget_alert['spent']:,.0f} so'm ({budget_alert['percent']:.1f}%)\n"
                    )
                elif budget_alert["status"] == "warning":
                    response += (
                        f"\n⚠️ **BYUDJET LIMITIGA YAQIN QOLDI! (80%+)**\n"
                        f"Limit: {budget_alert['limit']:,.0f} so'm\n"
                        f"Sarflangan: {budget_alert['spent']:,.0f} so'm ({budget_alert['percent']:.1f}%)\n"
                    )
            
            await message.answer(response)
        except Exception as e:
            await message.answer(f"❌ Xatolik yuz berdi: {e}")

@router.message(Command("t"))
async def cmd_quick_transaction(message: Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("⚠️ Namuna: `/t 15000 taksi` (avtomatik ravishda chiqim hisoblanadi)")
        return
    await process_quick_transaction(message, "expense", args[1])

@router.message(Command("kirim"))
async def cmd_quick_income(message: Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        # If no args, run interactive FSM
        from bot.handlers.income import start_income
        from aiogram.fsm.context import FSMContext
        # Note: We need state to trigger FSM. Since aiogram injects state we can let it go to interactive or guide
        await message.answer("⚠️ Tezkor kirim yozish uchun: `/kirim 500000 oylik` ko'rinishida yozing.")
        return
    await process_quick_transaction(message, "income", args[1])

@router.message(Command("chiqim"))
async def cmd_quick_expense(message: Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("⚠️ Tezkor chiqim yozish uchun: `/chiqim 15000 taksi` ko'rinishida yozing.")
        return
    await process_quick_transaction(message, "expense", args[1])
