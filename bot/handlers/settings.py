from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import Command

from bot.services.finance_service import finance_service
from bot.keyboards.inline import get_currency_keyboard

router = Router()

class CategoryCreateState(StatesGroup):
    name = State()
    type = State()
    icon = State()

@router.message(F.text == "⚙️ Sozlamalar")
@router.message(Command("sozlamalar"))
async def show_settings_menu(message: Message):
    user_id = message.from_user.id
    user = await finance_service.get_or_create_user(user_id)
    
    text = (
        f"⚙️ **BOT SOZLAMALARI**\n\n"
        f"👤 **Foydalanuvchi:** {user.full_name or 'Foydalanuvchi'}\n"
        f"💱 **Asosiy Valyuta:** {user.currency}\n"
        f"🌐 **Til:** O'zbekcha (UZ)\n"
        f"⏰ **Vaqt mintaqasi:** {user.timezone}\n\n"
        f"Quyidagi sozlamalarni o'zgartirishingiz mumkin:"
    )
    
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="💱 Valyutani o'zgartirish", callback_data="set_currency_menu"))
    builder.add(InlineKeyboardButton(text="➕ Kategoriya qo'shish", callback_data="add_custom_category"))
    builder.add(InlineKeyboardButton(text="💡 Buyruqlar ro'yxati (Yordam)", callback_data="help_menu"))
    builder.adjust(1)
    
    await message.answer(text, reply_markup=builder.as_markup())

@router.callback_query(F.data == "set_currency_menu")
async def cb_currency_menu(callback: CallbackQuery):
    await callback.answer()
    kb = get_currency_keyboard()
    # Add cancel back to settings row
    kb.inline_keyboard.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_settings")])
    await callback.message.edit_text("💱 **Yangi asosiy valyutani tanlang:**", reply_markup=kb)

@router.callback_query(F.data == "back_to_settings")
async def cb_back_to_settings(callback: CallbackQuery):
    await callback.answer()
    await callback.message.delete()
    # Send a mock message to settings
    await show_settings_menu(callback.message)

@router.callback_query(F.data == "help_menu")
async def cb_help_menu(callback: CallbackQuery):
    await callback.answer()
    from bot.handlers.start import cmd_help
    await cmd_help(callback.message)
    await callback.message.delete()

# --- CUSTOM CATEGORY FLOW ---

@router.callback_query(F.data == "add_custom_category")
async def cb_start_add_category(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    await state.set_state(CategoryCreateState.name)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_settings_state")]
    ])
    await callback.message.answer("📝 **Yangi kategoriya nomini kiriting** (Masalan: `Kuryerlik` yoki `Kollej`):", reply_markup=kb)

@router.callback_query(F.data == "cancel_settings_state")
async def cb_cancel_settings_state(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer("Amal bekor qilindi.")
    await callback.message.delete()

@router.message(CategoryCreateState.name)
async def process_cat_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await state.set_state(CategoryCreateState.type)
    
    buttons = [
        [InlineKeyboardButton(text="💰 Kirim (Income)", callback_data="cat_type_income"),
         InlineKeyboardButton(text="💸 Chiqim (Expense)", callback_data="cat_type_expense")],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_settings_state")]
    ]
    await message.answer("📌 **Kategoriya turini tanlang:**", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@router.callback_query(CategoryCreateState.type, F.data.startswith("cat_type_"))
async def process_cat_type(callback: CallbackQuery, state: FSMContext):
    cat_type = callback.data.split("_")[2]
    await state.update_data(type=cat_type)
    await state.set_state(CategoryCreateState.icon)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="O'tkazib yuborish (📌)", callback_data="cat_skip_icon")]
    ])
    await callback.message.edit_text("🎭 **Kategoriya uchun bitta Emoji kiriting** (Masalan: `🎬` yoki `💼`):", reply_markup=kb)

@router.callback_query(CategoryCreateState.icon, F.data == "cat_skip_icon")
@router.message(CategoryCreateState.icon)
async def process_cat_icon(event, state: FSMContext):
    icon = "📌"
    user_id = event.from_user.id
    
    if isinstance(event, Message):
        text = event.text.strip()
        # Take only the first character/emoji
        if text:
            icon = text[0]
        message = event
    else:
        await event.answer()
        message = event.message
        
    data = await state.get_data()
    
    try:
        category = await finance_service.create_category(
            user_id=user_id,
            name=data["name"],
            cat_type=data["type"],
            icon=icon
        )
        
        type_str = "Kirim" if category.type == "income" else "Chiqim"
        await message.answer(
            f"✅ **Kategoriya muvaffaqiyatli yaratildi!**\n\n"
            f"📌 **Nom:** {category.icon} {category.name}\n"
            f"🎭 **Tur:** {type_str}"
        )
    except Exception as e:
        await message.answer(f"❌ Xatolik yuz berdi: {e}")
        
    await state.clear()
