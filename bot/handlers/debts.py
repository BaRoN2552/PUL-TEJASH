import re
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import Command
from datetime import date

from bot.services.finance_service import finance_service

router = Router()

class DebtCreateState(StatesGroup):
    person_name = State()
    amount = State()
    currency = State()
    debt_type = State()
    description = State()

class DebtSettleState(StatesGroup):
    debt_id = State()
    account_id = State()

@router.message(F.text == "🤝 Qarzlar")
@router.message(Command("qarzlar"))
async def show_debts_menu(message: Message):
    user_id = message.from_user.id
    
    # Fetch active debts
    active_debts = await finance_service.get_debts(user_id, is_settled=False)
    
    given_total = 0.0
    received_total = 0.0
    
    given_text = ""
    received_text = ""
    
    builder = InlineKeyboardBuilder()
    
    for idx, d in enumerate(active_debts, 1):
        # We assume converted to UZS for net totals or represent in their native currency
        # For simplicity, represent in their native currency
        if d.type == "given":
            given_total += float(d.amount) # simplified summation
            desc_str = f" ({d.description})" if d.description else ""
            given_text += f"• {d.person_name}: {d.amount:,.0f} {d.currency}{desc_str}\n"
        else:
            received_total += float(d.amount)
            desc_str = f" ({d.description})" if d.description else ""
            received_text += f"• {d.person_name}: {d.amount:,.0f} {d.currency}{desc_str}\n"
            
        builder.add(InlineKeyboardButton(text=f"✅ Yopish: {d.person_name} ({d.amount:,.0f} {d.currency})", callback_data=f"settle_deb_{d.id}"))
        
    builder.adjust(1)
    builder.row(
        InlineKeyboardButton(text="➕ Berdim", callback_data="debt_add_given"),
        InlineKeyboardButton(text="➕ Oldim", callback_data="debt_add_received")
    )
    
    text = "🤝 **QARZLAR BOSHQARUVI**\n\n"
    text += f"➕ **Menga qarzdorlar (Berganlarim):**\n"
    text += given_text if given_text else "• Hozircha hech kim qarzli emas.\n"
    text += "\n"
    text += f"➖ **Men qarzdorlar (Olganlarim):**\n"
    text += received_text if received_text else "• Qarzlar yo'q.\n"
    
    await message.answer(text, reply_markup=builder.as_markup())

# --- QUICK DEBT SHORTHANDS ---

async def process_quick_debt(message: Message, debt_type: str, args_text: str):
    """Parses /berdim Akbar 200000 or /oldim Bobur 500000 'Biznes'"""
    user_id = message.from_user.id
    
    # Match person, amount, optional currency, and description
    match = re.match(r"^(\w+)\s+(\d+(?:\.\d+)?)\s*([A-Z]{3})?\s*(.*)$", args_text.strip(), re.IGNORECASE)
    if not match:
        await message.answer(
            f"⚠️ Format noto'g'ri. Namunalar:\n"
            f"• `/berdim Akbar 200000 Avtobus uchun`\n"
            f"• `/oldim Bobur 100 USD Biznes uchun`"
        )
        return
        
    person_name = match.group(1)
    amount = float(match.group(2))
    currency = (match.group(3) or "UZS").upper()
    description = match.group(4).strip()
    
    try:
        debt = await finance_service.create_debt(
            user_id=user_id,
            person_name=person_name,
            amount=amount,
            currency=currency,
            debt_type=debt_type,
            description=description
        )
        
        type_str = "berdingiz" if debt_type == "given" else "oldingiz"
        success_text = (
            f"✅ **Qarz muvaffaqiyatli yozildi!**\n\n"
            f"🤝 **Kimdan/Kimga:** {debt.person_name}\n"
            f"💰 **Miqdor:** {debt.amount:,.2f} {debt.currency}\n"
            f"📌 **Tur:** Qarz {type_str}\n"
        )
        if description:
            success_text += f"📝 **Tavsif:** {description}\n"
            
        await message.answer(success_text)
    except Exception as e:
        await message.answer(f"❌ Xatolik yuz berdi: {e}")

@router.message(Command("berdim"))
async def cmd_debt_given(message: Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("⚠️ Namuna: `/berdim Akbar 200000 Avtobus` (Akbarga 200 ming qarz berdingiz)")
        return
    await process_quick_debt(message, "given", args[1])

@router.message(Command("oldim"))
async def cmd_debt_received(message: Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("⚠️ Namuna: `/oldim Bobur 500000 Biznes` (Boburdan 500 ming qarz oldingiz)")
        return
    await process_quick_debt(message, "received", args[1])

# --- INTERACTIVE DEBT CREATION ---

@router.callback_query(F.data.startswith("debt_add_"))
async def cb_start_add_debt(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    debt_type = callback.data.split("_")[2] # given | received
    await state.clear()
    await state.set_state(DebtCreateState.person_name)
    await state.update_data(debt_type=debt_type)
    
    type_action = "qarz berdingiz?" if debt_type == "given" else "qarz oldingiz?"
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_debt")]
    ])
    await callback.message.answer(f"👤 **Kimga/Kimdan** {type_action} Ismini yozing:", reply_markup=kb)

@router.callback_query(F.data == "cancel_debt")
async def cancel_debt_flow(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer("Amal bekor qilindi.")
    await callback.message.delete()

@router.message(DebtCreateState.person_name)
async def process_debt_person(message: Message, state: FSMContext):
    await state.update_data(person_name=message.text.strip())
    await state.set_state(DebtCreateState.amount)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_debt")]
    ])
    await message.answer("💰 **Qarz miqdorini kiriting:**", reply_markup=kb)

@router.message(DebtCreateState.amount)
async def process_debt_amount(message: Message, state: FSMContext):
    text = message.text.strip().replace(" ", "")
    if not text.isdigit():
        await message.answer("⚠️ Miqdor faqat raqam bo'lishi kerak. Qaytadan kiriting:")
        return
        
    await state.update_data(amount=float(text))
    await state.set_state(DebtCreateState.currency)
    
    buttons = [
        [InlineKeyboardButton(text="UZS", callback_data="debt_cur_UZS"),
         InlineKeyboardButton(text="USD", callback_data="debt_cur_USD")],
        [InlineKeyboardButton(text="EUR", callback_data="debt_cur_EUR"),
         InlineKeyboardButton(text="RUB", callback_data="debt_cur_RUB")]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer("💱 **Valyutani tanlang:**", reply_markup=kb)

@router.callback_query(DebtCreateState.currency, F.data.startswith("debt_cur_"))
async def process_debt_currency(callback: CallbackQuery, state: FSMContext):
    currency = callback.data.split("_")[2]
    await state.update_data(currency=currency)
    await state.set_state(DebtCreateState.description)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➡️ O'tkazib yuborish", callback_data="debt_skip_desc")]
    ])
    await callback.message.edit_text("📝 **Batafsil tavsif yozing** (ixtiyoriy):", reply_markup=kb)

@router.callback_query(DebtCreateState.description, F.data == "debt_skip_desc")
@router.message(DebtCreateState.description)
async def process_debt_desc(event, state: FSMContext):
    description = ""
    user_id = event.from_user.id
    
    if isinstance(event, Message):
        description = event.text.strip()
        message = event
    else:
        await event.answer()
        message = event.message
        
    data = await state.get_data()
    
    try:
        debt = await finance_service.create_debt(
            user_id=user_id,
            person_name=data["person_name"],
            amount=data["amount"],
            currency=data["currency"],
            debt_type=data["debt_type"],
            description=description
        )
        
        type_str = "berilgan" if data["debt_type"] == "given" else "olingan"
        success_text = (
            f"✅ **Qarz muvaffaqiyatli yaratildi!**\n\n"
            f"🤝 **Hamkor:** {debt.person_name}\n"
            f"💰 **Miqdor:** {debt.amount:,.0f} {debt.currency}\n"
            f"📌 **Turi:** Qarz {type_str}\n"
        )
        if description:
            success_text += f"📝 **Tavsif:** {description}\n"
            
        if isinstance(event, CallbackQuery):
            await message.edit_text(success_text)
        else:
            await message.answer(success_text)
    except Exception as e:
        if isinstance(event, CallbackQuery):
            await message.edit_text(f"❌ Xatolik: {e}")
        else:
            await message.answer(f"❌ Xatolik: {e}")
            
    await state.clear()

# --- DEBT SETTLEMENT ---

@router.callback_query(F.data.startswith("settle_deb_"))
async def cb_start_settle_debt(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    debt_id = int(callback.data.split("_")[2])
    
    await state.clear()
    await state.set_state(DebtSettleState.debt_id)
    await state.update_data(debt_id=debt_id)
    
    # Ask if they want to adjust accounts or just mark it settled
    accounts = await finance_service.get_user_accounts(callback.from_user.id)
    builder = InlineKeyboardBuilder()
    for acc in accounts:
        builder.add(InlineKeyboardButton(text=f"⚖️ {acc.icon} {acc.name} balansiga ta'sir qilsin", callback_data=f"debt_settle_acc_{acc.id}"))
    builder.adjust(1)
    builder.row(InlineKeyboardButton(text="Mark as Settled (Balansga ta'sirsiz)", callback_data="debt_settle_acc_none"))
    builder.row(InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_debt"))
    
    await callback.message.answer(
        "⚖️ **Qarzni qanday yopamiz?**\n"
        "Qarz yopilganda biror hisobingizdan mablag' yechilishi/qo'shilishini xohlaysizmi?",
        reply_markup=builder.as_markup()
    )

@router.callback_query(DebtSettleState.debt_id, F.data.startswith("debt_settle_acc_"))
async def cb_process_settle_account(callback: CallbackQuery, state: FSMContext):
    acc_val = callback.data.split("_")[3]
    acc_id = None if acc_val == "none" else int(acc_val)
    
    data = await state.get_data()
    user_id = callback.from_user.id
    
    success, message_text = await finance_service.settle_debt(
        user_id=user_id,
        debt_id=data["debt_id"],
        account_id=acc_id
    )
    
    if success:
        await callback.message.edit_text(f"✅ {message_text}")
    else:
        await callback.message.edit_text(f"❌ Xatolik: {message_text}")
        
    await state.clear()
