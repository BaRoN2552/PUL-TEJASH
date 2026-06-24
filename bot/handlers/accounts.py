from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import Command

from bot.services.finance_service import finance_service
from bot.services.currency_service import currency_service
from bot.keyboards.inline import get_account_type_keyboard, get_currency_keyboard

router = Router()

class AccountCreateState(StatesGroup):
    name = State()
    type = State()
    currency = State()
    balance = State()

class TransferState(StatesGroup):
    from_account = State()
    to_account = State()
    amount = State()

@router.message(F.text == "💵 Balans")
@router.message(Command("balans"))
async def show_accounts_balances(message: Message):
    user_id = message.from_user.id
    accounts = await finance_service.get_user_accounts(user_id)
    user = await finance_service.get_or_create_user(user_id)
    
    if not accounts:
        await message.answer("❌ Hisoblaringiz topilmadi. Avval `/start` buyrug'ini yuboring.")
        return

    text = "💵 **HISOBINGIZ BALANSLARI:**\n\n"
    total_in_base = 0.0
    
    builder = InlineKeyboardBuilder()
    
    for acc in accounts:
        # Convert balance to user's preferred primary currency to calculate Net Total
        converted = await currency_service.convert(float(acc.balance), acc.currency, user.currency)
        total_in_base += converted
        
        text += f"{acc.icon or '💰'} **{acc.name}** ({acc.type.capitalize()}):\n"
        text += f"└ {acc.balance:,.2f} {acc.currency}\n"
        if acc.currency != user.currency:
            text += f"└ ~{converted:,.2f} {user.currency}\n"
        text += "\n"
        
    text += f"📈 **Umumiy Balans:** {total_in_base:,.2f} {user.currency}"
    
    builder.add(InlineKeyboardButton(text="➕ Yangi hisob qo'shish", callback_data="acc_add"))
    builder.add(InlineKeyboardButton(text="🔄 Hisoblararo transfer", callback_data="acc_transfer"))
    builder.adjust(2)
    
    await message.answer(text, reply_markup=builder.as_markup())

# --- CREATE ACCOUNT FLOW ---

@router.callback_query(F.data == "acc_add")
async def start_add_account(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    await state.set_state(AccountCreateState.name)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_acc")]
    ])
    await callback.message.answer("💳 **Yangi hisob nomini kiriting** (Masalan: `Kapitalbank Karta` yoki `Payme`):", reply_markup=kb)

@router.callback_query(F.data == "cancel_acc")
async def cancel_account_flow(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer("Amal bekor qilindi.")
    await callback.message.delete()

@router.message(AccountCreateState.name)
async def process_account_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await state.set_state(AccountCreateState.type)
    
    kb = get_account_type_keyboard()
    # Add cancel row
    kb.inline_keyboard.append([InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_acc")])
    await message.answer("📁 **Hisob turini tanlang:**", reply_markup=kb)

@router.callback_query(AccountCreateState.type, F.data.startswith("acc_type_"))
async def process_account_type(callback: CallbackQuery, state: FSMContext):
    acc_type = callback.data.split("_")[2]
    await state.update_data(type=acc_type)
    await state.set_state(AccountCreateState.currency)
    
    kb = get_currency_keyboard()
    kb.inline_keyboard.append([InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_acc")])
    await callback.message.edit_text("💱 **Hisob valyutasini tanlang:**", reply_markup=kb)

@router.callback_query(AccountCreateState.currency, F.data.startswith("set_currency_"))
async def process_account_currency(callback: CallbackQuery, state: FSMContext):
    currency = callback.data.split("_")[2]
    await state.update_data(currency=currency)
    await state.set_state(AccountCreateState.balance)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_acc")]
    ])
    await callback.message.edit_text("💰 **Hisobdagi dastlabki qoldiqni kiriting** (Masalan: `500000` yoki `0`):", reply_markup=kb)

@router.message(AccountCreateState.balance)
async def process_account_balance(message: Message, state: FSMContext):
    text = message.text.strip().replace(" ", "")
    if not text.isdigit():
        await message.answer("⚠️ Miqdor faqat raqam bo'lishi kerak. Qayta kiriting:")
        return
        
    data = await state.get_data()
    user_id = message.from_user.id
    
    # Assign beautiful icons based on type
    icons = {"cash": "💵", "card": "💳", "wallet": "📱"}
    icon = icons.get(data["type"], "💰")
    
    try:
        acc = await finance_service.create_account(
            user_id=user_id,
            name=data["name"],
            account_type=data["type"],
            currency=data["currency"],
            balance=float(text),
            icon=icon
        )
        
        await message.answer(
            f"✅ **Yangi hisob yaratildi!**\n\n"
            f"💳 **Hisob:** {acc.icon} {acc.name}\n"
            f"💰 **Balans:** {acc.balance:,.2f} {acc.currency}\n"
            f"📌 **Turi:** {acc.type.upper()}"
        )
    except Exception as e:
        await message.answer(f"❌ Xatolik yuz berdi: {e}")
        
    await state.clear()

# --- TRANSFER FLOW ---

@router.message(Command("transfer"))
async def cmd_transfer(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(TransferState.from_account)
    
    accounts = await finance_service.get_user_accounts(message.from_user.id)
    builder = InlineKeyboardBuilder()
    for acc in accounts:
        builder.add(InlineKeyboardButton(text=f"{acc.icon} {acc.name} ({acc.balance:,.0f} {acc.currency})", callback_data=f"tr_from_{acc.id}"))
    builder.adjust(1)
    builder.row(InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_acc"))
    
    await message.answer("🔄 **Mablag' qaysi hisobdan o'tkaziladi?** Tanlang:", reply_markup=builder.as_markup())

@router.callback_query(F.data == "acc_transfer")
async def cb_start_transfer(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    await state.set_state(TransferState.from_account)
    
    accounts = await finance_service.get_user_accounts(callback.from_user.id)
    builder = InlineKeyboardBuilder()
    for acc in accounts:
        builder.add(InlineKeyboardButton(text=f"{acc.icon} {acc.name} ({acc.balance:,.0f} {acc.currency})", callback_data=f"tr_from_{acc.id}"))
    builder.adjust(1)
    builder.row(InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_acc"))
    
    await callback.message.answer("🔄 **Mablag' qaysi hisobdan o'tkaziladi?** Tanlang:", reply_markup=builder.as_markup())

@router.callback_query(TransferState.from_account, F.data.startswith("tr_from_"))
async def process_transfer_from(callback: CallbackQuery, state: FSMContext):
    acc_id = int(callback.data.split("_")[2])
    await state.update_data(from_account=acc_id)
    await state.set_state(TransferState.to_account)
    
    accounts = await finance_service.get_user_accounts(callback.from_user.id)
    builder = InlineKeyboardBuilder()
    for acc in accounts:
        if acc.id != acc_id:
            builder.add(InlineKeyboardButton(text=f"{acc.icon} {acc.name} ({acc.balance:,.0f} {acc.currency})", callback_data=f"tr_to_{acc.id}"))
    builder.adjust(1)
    builder.row(InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_acc"))
    
    await callback.message.edit_text("🔄 **Qaysi hisobga o'tkaziladi?** Tanlang:", reply_markup=builder.as_markup())

@router.callback_query(TransferState.to_account, F.data.startswith("tr_to_"))
async def process_transfer_to(callback: CallbackQuery, state: FSMContext):
    acc_id = int(callback.data.split("_")[2])
    await state.update_data(to_account=acc_id)
    await state.set_state(TransferState.amount)
    
    from_data = await state.get_data()
    acc_from = await finance_service.get_account(from_data["from_account"])
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_acc")]
    ])
    await callback.message.edit_text(
        f"💰 **O'tkazma summasini kiriting** ({acc_from.currency} da, masalan: `100000`):",
        reply_markup=kb
    )

@router.message(TransferState.amount)
async def process_transfer_amount(message: Message, state: FSMContext):
    text = message.text.strip().replace(" ", "")
    if not text.isdigit():
        await message.answer("⚠️ Miqdor faqat raqam bo'lishi kerak. Qayta kiriting:")
        return
        
    amount = float(text)
    data = await state.get_data()
    user_id = message.from_user.id
    
    success, result_message = await finance_service.transfer_funds(
        user_id=user_id,
        from_acc_id=data["from_account"],
        to_acc_id=data["to_account"],
        amount=amount
    )
    
    if success:
        await message.answer(f"✅ {result_message}")
    else:
        await message.answer(f"❌ Xatolik: {result_message}")
        
    await state.clear()
