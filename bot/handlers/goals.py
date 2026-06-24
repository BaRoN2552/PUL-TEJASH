from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from datetime import datetime, date

from bot.services.finance_service import finance_service
from bot.keyboards.inline import get_currency_keyboard

router = Router()

class GoalCreateState(StatesGroup):
    name = State()
    amount = State()
    currency = State()
    deadline = State()

class GoalSaveState(StatesGroup):
    goal_id = State()
    amount = State()
    account_id = State()

def make_goal_progress_bar(percent: float) -> str:
    filled = min(10, int(percent / 10))
    empty = 10 - filled
    return "🔵" * filled + "⚪" * empty

@router.message(F.text == "🎯 Maqsadlar")
@router.message(F.text == "/maqsadlar")
async def show_goals_list(message: Message):
    user_id = message.from_user.id
    goals = await finance_service.get_goals(user_id)
    
    if not goals:
        text = (
            "🎯 **Moliyaviy maqsadlar**\n\n"
            "Siz hali hech qanday maqsad qo'shmabsiz (Masalan: Yangi noutbuk, Sayohat va h.k.).\n"
            "Maqsad qo'yish unga maqsadli va tizimli ravishda pul yig'ishga yordam beradi.\n\n"
            "Yangi maqsad qo'shish uchun quyidagi tugmani bosing:"
        )
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="➕ Yangi maqsad", callback_data="add_goal")]
        ])
        await message.answer(text, reply_markup=kb)
        return

    text = "🎯 **MOLIYAVIY MAQSADLARINGIZ HOLATI:**\n\n"
    builder = InlineKeyboardBuilder()
    
    active_goals_exist = False
    for g in goals:
        pct = (float(g.current_amount) / float(g.target_amount) * 100) if g.target_amount > 0 else 0
        p_bar = make_goal_progress_bar(pct)
        status = "✅ Erisildi!" if g.is_achieved else "⏳ Yig'ilmoqda..."
        
        text += (
            f"🎯 **{g.name}** ({status})\n"
            f"└ {p_bar} ({pct:.1f}%)\n"
            f"└ Jamg'arildi: {g.current_amount:,.0f} / {g.target_amount:,.0f} {g.currency}\n"
        )
        if g.deadline:
            text += f"└ Muddat: {g.deadline.strftime('%d.%m.%Y')}\n"
        text += "\n"
        
        if not g.is_achieved:
            builder.add(InlineKeyboardButton(text=f"💰 '{g.name}'ga yig'ish", callback_data=f"save_goal_{g.id}"))
            active_goals_exist = True
            
    builder.adjust(1)
    builder.row(InlineKeyboardButton(text="➕ Yangi maqsad", callback_data="add_goal"))
    
    await message.answer(text, reply_markup=builder.as_markup())

# --- GOAL CREATION ---

@router.callback_query(F.data == "add_goal")
async def start_add_goal(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    await state.set_state(GoalCreateState.name)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_goal")]
    ])
    await callback.message.answer("🎯 **Yangi maqsad nomini kiriting** (Masalan: `Yangi noutbuk`):", reply_markup=kb)

@router.callback_query(F.data == "cancel_goal")
async def cancel_goal_flow(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer("Amal bekor qilindi.")
    await callback.message.delete()

@router.message(GoalCreateState.name)
async def process_goal_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await state.set_state(GoalCreateState.amount)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_goal")]
    ])
    await message.answer("💰 **Kerakli bo'lgan maqsadli summani kiriting** (Faqat raqam, masalan: `10000000`):", reply_markup=kb)

@router.message(GoalCreateState.amount)
async def process_goal_amount(message: Message, state: FSMContext):
    text = message.text.strip().replace(" ", "")
    if not text.isdigit():
        await message.answer("⚠️ Miqdor faqat raqamlardan iborat bo'lishi kerak. Qayta kiriting:")
        return
        
    await state.update_data(amount=float(text))
    await state.set_state(GoalCreateState.currency)
    
    # Render inline currency selection
    buttons = [
        [InlineKeyboardButton(text="UZS", callback_data="goal_cur_UZS"),
         InlineKeyboardButton(text="USD", callback_data="goal_cur_USD")],
        [InlineKeyboardButton(text="EUR", callback_data="goal_cur_EUR"),
         InlineKeyboardButton(text="RUB", callback_data="goal_cur_RUB")]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer("💱 **Maqsad valyutasini tanlang:**", reply_markup=kb)

@router.callback_query(GoalCreateState.currency, F.data.startswith("goal_cur_"))
async def process_goal_currency(callback: CallbackQuery, state: FSMContext):
    currency = callback.data.split("_")[2]
    await state.update_data(currency=currency)
    await state.set_state(GoalCreateState.deadline)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➡️ O'tkazib yuborish", callback_data="goal_skip_deadline")]
    ])
    await callback.message.edit_text(
        "📅 **Maqsad oxirgi muddatini kiriting** (Format: `YYYY-MM-DD`, masalan: `2026-12-31`):",
        reply_markup=kb
    )

@router.callback_query(GoalCreateState.deadline, F.data == "goal_skip_deadline")
@router.message(GoalCreateState.deadline)
async def process_goal_deadline(event, state: FSMContext):
    deadline_date = None
    
    if isinstance(event, Message):
        text = event.text.strip()
        try:
            deadline_date = datetime.strptime(text, "%Y-%m-%d").date()
        except ValueError:
            await event.answer("⚠️ Muddat formati noto'g'ri. Iltimos `YYYY-MM-DD` ko'rinishida yozing yoki O'tkazib yuborishni bosing:")
            return
        message = event
    else:
        await event.answer()
        message = event.message
        
    data = await state.get_data()
    user_id = event.from_user.id
    
    try:
        goal = await finance_service.create_goal(
            user_id=user_id,
            name=data["name"],
            target_amount=data["amount"],
            currency=data["currency"],
            deadline=deadline_date
        )
        
        success_text = (
            f"✅ **Yangi maqsad yaratildi!**\n\n"
            f"🎯 **Maqsad:** {goal.name}\n"
            f"💰 **Suma:** {goal.target_amount:,.0f} {goal.currency}\n"
        )
        if goal.deadline:
            success_text += f"📅 **Muddat:** {goal.deadline.strftime('%d.%m.%Y')}\n"
            
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

# --- ADD SAVINGS TO GOAL ---

@router.callback_query(F.data.startswith("save_goal_"))
async def start_save_goal(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    goal_id = int(callback.data.split("_")[2])
    await state.clear()
    await state.set_state(GoalSaveState.goal_id)
    await state.update_data(goal_id=goal_id)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_goal")]
    ])
    await callback.message.answer("💰 **Ushbu maqsadga qancha pul jamg'armoqchisiz?** Summani kiriting:", reply_markup=kb)

@router.message(GoalSaveState.amount)
async def process_save_amount(message: Message, state: FSMContext):
    text = message.text.strip().replace(" ", "")
    if not text.isdigit():
        await message.answer("⚠️ Miqdor faqat raqam bo'lishi kerak. Qaytadan kiriting:")
        return
        
    await state.update_data(amount=float(text))
    await state.set_state(GoalSaveState.account_id)
    
    # Show source accounts
    accounts = await finance_service.get_user_accounts(message.from_user.id)
    builder = InlineKeyboardBuilder()
    for acc in accounts:
        builder.add(InlineKeyboardButton(text=f"{acc.icon or '💰'} {acc.name} ({acc.balance:,.0f} {acc.currency})", callback_data=f"goal_src_acc_{acc.id}"))
    builder.adjust(1)
    builder.row(InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_goal"))
    
    await message.answer("💳 **Qaysi hisobdan pul o'tkazasiz?** Tanlang:", reply_markup=builder.as_markup())

@router.callback_query(GoalSaveState.account_id, F.data.startswith("goal_src_acc_"))
async def process_save_source_account(callback: CallbackQuery, state: FSMContext):
    acc_id = int(callback.data.split("_")[3])
    data = await state.get_data()
    
    user_id = callback.from_user.id
    
    success, message_text = await finance_service.add_savings_to_goal(
        user_id=user_id,
        goal_id=data["goal_id"],
        amount=data["amount"],
        account_id=acc_id
    )
    
    if success:
        await callback.message.edit_text(f"✅ {message_text}")
    else:
        await callback.message.edit_text(f"❌ Xatolik: {message_text}")
        
    await state.clear()
