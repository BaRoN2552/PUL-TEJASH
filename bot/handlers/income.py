from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.services.finance_service import finance_service

router = Router()

class IncomeState(StatesGroup):
    amount = State()
    currency = State()
    category = State()
    description = State()
    account = State()

async def get_categories_keyboard(user_id: int) -> InlineKeyboardMarkup:
    categories = await finance_service.get_categories(user_id, "income")
    builder = InlineKeyboardBuilder()
    for cat in categories:
        builder.add(InlineKeyboardButton(text=f"{cat.icon or '📌'} {cat.name}", callback_data=f"select_cat_{cat.id}"))
    builder.adjust(2)
    return builder.as_markup()

async def get_accounts_keyboard(user_id: int) -> InlineKeyboardMarkup:
    accounts = await finance_service.get_user_accounts(user_id)
    builder = InlineKeyboardBuilder()
    for acc in accounts:
        builder.add(InlineKeyboardButton(text=f"{acc.icon or '💰'} {acc.name} ({acc.balance:,.0f} {acc.currency})", callback_data=f"select_acc_{acc.id}"))
    builder.adjust(1)
    return builder.as_markup()

@router.message(F.text == "💰 Kirim")
@router.message(F.text == "/kirim")
async def start_income(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(IncomeState.amount)
    
    # Cancel button
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_income")]
    ])
    await message.answer("💰 **Kirim miqdorini kiriting** (Masalan: `50000` yoki `10 USD`):", reply_markup=kb)

@router.callback_query(F.data == "cancel_income")
async def cancel_income_flow(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer("Amal bekor qilindi.")
    await callback.message.edit_text("💸 Kirim qo'shish jarayoni bekor qilindi.")

@router.message(IncomeState.amount)
async def process_amount(message: Message, state: FSMContext):
    text = message.text.strip().replace(" ", "").upper()
    
    # Try parsing amount and optional currency
    import re
    match = re.match(r"^(\d+(?:\.\d+)?)\s*([A-Z]{3})?$", text)
    if not match:
        await message.answer("⚠️ Miqdor noto'g'ri kiritildi. Iltimos faqat raqam yoki raqam va valyuta kodini kiriting (Masalan: `100000` yoki `20 USD`):")
        return
        
    amount = float(match.group(1))
    currency = match.group(2) or "UZS"
    
    await state.update_data(amount=amount, currency=currency)
    await state.set_state(IncomeState.category)
    
    kb = await get_categories_keyboard(message.from_user.id)
    await message.answer("📌 **Kirim kategoriyasini tanlang:**", reply_markup=kb)

@router.callback_query(IncomeState.category, F.data.startswith("select_cat_"))
async def process_category(callback: CallbackQuery, state: FSMContext):
    cat_id = int(callback.data.split("_")[2])
    await state.update_data(category_id=cat_id)
    
    await state.set_state(IncomeState.description)
    
    # Skip description button
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➡️ O'tkazib yuborish", callback_data="skip_desc")]
    ])
    await callback.message.edit_text("📝 **Kirim uchun tavsif yozing** (ixtiyoriy):", reply_markup=kb)

@router.callback_query(IncomeState.description, F.data == "skip_desc")
@router.message(IncomeState.description)
async def process_description(event, state: FSMContext):
    # event can be Message or CallbackQuery
    description = ""
    user_id = None
    
    if isinstance(event, CallbackQuery):
        user_id = event.from_user.id
        await event.answer()
        message = event.message
    else:
        user_id = event.from_user.id
        description = event.text.strip()
        message = event
        
    await state.update_data(description=description)
    await state.set_state(IncomeState.account)
    
    kb = await get_accounts_keyboard(user_id)
    
    if isinstance(event, CallbackQuery):
        await message.edit_text("💳 **Mablag' qaysi hisobga tushadi?** Tanlang:", reply_markup=kb)
    else:
        await message.answer("💳 **Mablag' qaysi hisobga tushadi?** Tanlang:", reply_markup=kb)

@router.callback_query(IncomeState.account, F.data.startswith("select_acc_"))
async def process_account(callback: CallbackQuery, state: FSMContext):
    acc_id = int(callback.data.split("_")[2])
    data = await state.get_data()
    
    user_id = callback.from_user.id
    
    try:
        # Create transaction
        tx, _ = await finance_service.create_transaction(
            user_id=user_id,
            account_id=acc_id,
            category_id=data["category_id"],
            tx_type="income",
            amount=data["amount"],
            currency=data["currency"],
            description=data["description"]
        )
        
        # Get category & account info
        category = await finance_service.get_category(data["category_id"])
        account = await finance_service.get_account(acc_id)
        
        success_text = (
            f"✅ **Kirim muvaffaqiyatli saqlandi!**\n\n"
            f"💰 **Miqdor:** {data['amount']:,.2f} {data['currency']}\n"
            f"📌 **Kategoriya:** {category.icon or '📌'} {category.name}\n"
            f"💳 **Hisob:** {account.icon or '💰'} {account.name}\n"
        )
        if data["description"]:
            success_text += f"📝 **Tavsif:** {data['description']}\n"
            
        await callback.message.edit_text(success_text)
    except Exception as e:
        await callback.message.edit_text(f"❌ Xatolik yuz berdi: {e}")
        
    await state.clear()
