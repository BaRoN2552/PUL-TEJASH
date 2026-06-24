from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.services.finance_service import finance_service

router = Router()

class BudgetState(StatesGroup):
    category = State()
    amount = State()

def make_progress_bar(percent: float) -> str:
    filled = min(10, int(percent / 10))
    empty = 10 - filled
    if percent >= 100:
        return "🟥" * 10
    elif percent >= 80:
        return "🟨" * filled + "⬜" * empty
    else:
        return "🟩" * filled + "⬜" * empty

@router.message(F.text == "📅 Byudjet")
@router.message(F.text == "/byudjet")
async def show_budget_status(message: Message):
    user_id = message.from_user.id
    status_list = await finance_service.get_budgets_status(user_id)
    
    if not status_list:
        text = (
            "📅 **Byudjet boshqaruvi**\n\n"
            "Siz hali oylik byudjet limitlarini o'rnatmabsiz. "
            "Kategoriyalar bo'yicha limit qo'yish moliyaviy intizomni yaxshilaydi.\n\n"
            "Limit qo'shish uchun quyidagi tugmani bosing:"
        )
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="➕ Byudjet belgilash", callback_data="add_budget")]
        ])
        await message.answer(text, reply_markup=kb)
        return

    text = "📅 **OYLIK BYUDJETLAR HOLATI:**\n\n"
    for b in status_list:
        p_bar = make_progress_bar(b["percent"])
        remaining = b["limit"] - b["spent"]
        rem_text = f"Qoldi: {remaining:,.0f} so'm" if remaining >= 0 else f"Oshib ketdi: {abs(remaining):,.0f} so'm ⚠️"
        
        text += (
            f"{b['category_icon']} **{b['category_name']}**\n"
            f"└ {p_bar} ({b['percent']}%)\n"
            f"└ Limit: {b['limit']:,.0f} | Spent: {b['spent']:,.0f}\n"
            f"└ {rem_text}\n\n"
        )

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Limit qo'shish / o'zgartirish", callback_data="add_budget")]
    ])
    await message.answer(text, reply_markup=kb)

@router.callback_query(F.data == "add_budget")
async def start_add_budget(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    await state.set_state(BudgetState.category)
    
    # Show expense categories
    categories = await finance_service.get_categories(callback.from_user.id, "expense")
    builder = InlineKeyboardBuilder()
    for cat in categories:
        builder.add(InlineKeyboardButton(text=f"{cat.icon or '📌'} {cat.name}", callback_data=f"set_bud_cat_{cat.id}"))
    builder.adjust(2)
    builder.row(InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_budget"))
    
    await callback.message.answer("📌 **Byudjet qo'yiladigan kategoriyani tanlang:**", reply_markup=builder.as_markup())

@router.callback_query(F.data == "cancel_budget")
async def cancel_budget_flow(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer("Amal bekor qilindi.")
    await callback.message.delete()

@router.callback_query(BudgetState.category, F.data.startswith("set_bud_cat_"))
async def process_budget_category(callback: CallbackQuery, state: FSMContext):
    cat_id = int(callback.data.split("_")[3])
    await state.update_data(category_id=cat_id)
    await state.set_state(BudgetState.amount)
    
    category = await finance_service.get_category(cat_id)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_budget")]
    ])
    await callback.message.edit_text(
        f"📅 **{category.icon} {category.name}** kategoriyasi uchun **oylik limit summasini** kiriting (so'mda, masalan: `1000000`):",
        reply_markup=kb
    )

@router.message(BudgetState.amount)
async def process_budget_amount(message: Message, state: FSMContext):
    text = message.text.strip().replace(" ", "")
    
    if not text.isdigit():
        await message.answer("⚠️ Limit faqat raqam bo'lishi kerak. Qaytadan kiriting (Masalan: `500000`):")
        return
        
    amount = float(text)
    data = await state.get_data()
    user_id = message.from_user.id
    
    try:
        budget = await finance_service.set_budget(
            user_id=user_id,
            category_id=data["category_id"],
            amount=amount
        )
        category = await finance_service.get_category(data["category_id"])
        
        success_text = (
            f"✅ **Oylik byudjet o'rnatildi!**\n\n"
            f"📌 **Kategoriya:** {category.icon} {category.name}\n"
            f"💰 **Oylik limit:** {amount:,.0f} so'm\n"
            f"⏰ **Davr:** Joriy oy"
        )
        await message.answer(success_text)
    except Exception as e:
        await message.answer(f"❌ Xatolik: {e}")
        
    await state.clear()
