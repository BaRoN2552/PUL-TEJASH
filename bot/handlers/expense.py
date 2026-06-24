from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.services.finance_service import finance_service

router = Router()

class ExpenseState(StatesGroup):
    amount = State()
    currency = State()
    category = State()
    description = State()
    account = State()

async def get_categories_keyboard(user_id: int) -> InlineKeyboardMarkup:
    categories = await finance_service.get_categories(user_id, "expense")
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

@router.message(F.text == "💸 Chiqim")
@router.message(F.text == "/chiqim")
async def start_expense(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(ExpenseState.amount)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_expense")]
    ])
    await message.answer("💸 **Chiqim miqdorini kiriting** (Masalan: `15000` yoki `5 USD`):", reply_markup=kb)

@router.callback_query(F.data == "cancel_expense")
async def cancel_expense_flow(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer("Amal bekor qilindi.")
    await callback.message.edit_text("💸 Chiqim qo'shish jarayoni bekor qilindi.")

@router.message(ExpenseState.amount)
async def process_amount(message: Message, state: FSMContext):
    text = message.text.strip().replace(" ", "").upper()
    
    import re
    match = re.match(r"^(\d+(?:\.\d+)?)\s*([A-Z]{3})?$", text)
    if not match:
        await message.answer("⚠️ Miqdor noto'g'ri kiritildi. Iltimos faqat raqam yoki raqam va valyuta kodini kiriting (Masalan: `50000` yoki `10 USD`):")
        return
        
    amount = float(match.group(1))
    currency = match.group(2) or "UZS"
    
    await state.update_data(amount=amount, currency=currency)
    await state.set_state(ExpenseState.category)
    
    kb = await get_categories_keyboard(message.from_user.id)
    await message.answer("📌 **Chiqim kategoriyasini tanlang:**", reply_markup=kb)

@router.callback_query(ExpenseState.category, F.data.startswith("select_cat_"))
async def process_category(callback: CallbackQuery, state: FSMContext):
    cat_id = int(callback.data.split("_")[2])
    await state.update_data(category_id=cat_id)
    
    await state.set_state(ExpenseState.description)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➡️ O'tkazib yuborish", callback_data="skip_desc")]
    ])
    await callback.message.edit_text("📝 **Chiqim uchun tavsif yozing** (ixtiyoriy):", reply_markup=kb)

@router.callback_query(ExpenseState.description, F.data == "skip_desc")
@router.message(ExpenseState.description)
async def process_description(event, state: FSMContext):
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
    await state.set_state(ExpenseState.account)
    
    kb = await get_accounts_keyboard(user_id)
    
    if isinstance(event, CallbackQuery):
        await message.edit_text("💳 **Chiqim qaysi hisobdan to'lanadi?** Tanlang:", reply_markup=kb)
    else:
        await message.answer("💳 **Chiqim qaysi hisobdan to'lanadi?** Tanlang:", reply_markup=kb)

@router.callback_query(ExpenseState.account, F.data.startswith("select_acc_"))
async def process_account(callback: CallbackQuery, state: FSMContext):
    acc_id = int(callback.data.split("_")[2])
    data = await state.get_data()
    
    user_id = callback.from_user.id
    
    try:
        # Create transaction and check budget limit alert
        tx, budget_alert = await finance_service.create_transaction(
            user_id=user_id,
            account_id=acc_id,
            category_id=data["category_id"],
            tx_type="expense",
            amount=data["amount"],
            currency=data["currency"],
            description=data["description"]
        )
        
        category = await finance_service.get_category(data["category_id"])
        account = await finance_service.get_account(acc_id)
        
        success_text = (
            f"✅ **Chiqim muvaffaqiyatli saqlandi!**\n\n"
            f"💸 **Miqdor:** {data['amount']:,.2f} {data['currency']}\n"
            f"📌 **Kategoriya:** {category.icon or '📌'} {category.name}\n"
            f"💳 **Hisob:** {account.icon or '💰'} {account.name}\n"
        )
        if data["description"]:
            success_text += f"📝 **Tavsif:** {data['description']}\n"
            
        # Append budget alerts if any
        if budget_alert:
            if budget_alert["status"] == "exceeded":
                success_text += (
                    f"\n🚨 **DIQQAT! BYUDJET LIMITI OSHIB KETDI!**\n"
                    f"Kategoriya: {category.icon or '📌'} {category.name}\n"
                    f"Limit: {budget_alert['limit']:,.0f} so'm\n"
                    f"Ishlatildi: {budget_alert['spent']:,.0f} so'm ({budget_alert['percent']:.1f}%)\n"
                )
            elif budget_alert["status"] == "warning":
                success_text += (
                    f"\n⚠️ **OGOHLANTIRISH! BYUDJET LIMITIGA YAQIN QOLDI! (80%+)**\n"
                    f"Kategoriya: {category.icon or '📌'} {category.name}\n"
                    f"Limit: {budget_alert['limit']:,.0f} so'm\n"
                    f"Ishlatildi: {budget_alert['spent']:,.0f} so'm ({budget_alert['percent']:.1f}%)\n"
                )

        await callback.message.edit_text(success_text)
    except Exception as e:
        await callback.message.edit_text(f"❌ Xatolik yuz berdi: {e}")
        
    await state.clear()
