from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import Command
from datetime import date, timedelta
import os

from bot.keyboards.inline import get_reports_keyboard
from bot.services.report_service import report_service
from bot.services.ai_service import ai_service

router = Router()

@router.message(F.text == "📊 Hisobotlar")
async def show_reports_menu(message: Message):
    await message.answer(
        "📊 **Hisobotlar bo'limi**\n\n"
        "Qaysi davr uchun hisobotni ko'rmoqchisiz? Tanlang:",
        reply_markup=get_reports_keyboard()
    )

@router.message(Command("kun"))
async def cmd_report_daily(message: Message):
    text, chart_path = await report_service.generate_daily_report(message.from_user.id)
    if chart_path and os.path.exists(chart_path):
        await message.answer_photo(photo=FSInputFile(chart_path), caption=text)
    else:
        await message.answer(text)

@router.message(Command("hafta"))
async def cmd_report_weekly(message: Message):
    text, chart_path = await report_service.generate_weekly_report(message.from_user.id)
    if chart_path and os.path.exists(chart_path):
        await message.answer_photo(photo=FSInputFile(chart_path), caption=text)
    else:
        await message.answer(text)

@router.message(Command("oy"))
async def cmd_report_monthly(message: Message):
    text, chart_path = await report_service.generate_monthly_report(message.from_user.id)
    if chart_path and os.path.exists(chart_path):
        await message.answer_photo(photo=FSInputFile(chart_path), caption=text)
    else:
        await message.answer(text)

@router.message(Command("maslahat"))
async def cmd_report_ai(message: Message):
    await message.answer("🤖 AI tahlil qilmoqda, iltimos kuting...")
    advice = await ai_service.get_financial_advice(message.from_user.id)
    await message.answer(advice)

@router.message(Command("eksport"))
async def cmd_report_excel(message: Message):
    await message.answer("📤 Excel fayli tayyorlanmoqda...")
    end_date = date.today()
    start_date = end_date - timedelta(days=30)
    file_path = await report_service.export_to_excel(message.from_user.id, start_date, end_date)
    
    if file_path and os.path.exists(file_path):
        await message.answer_document(
            document=FSInputFile(file_path),
            caption=f"📊 Oxirgi 30 kunlik tranzaksiyalar hisoboti ({start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')})"
        )
    else:
        await message.answer("❌ Ushbu davrda hech qanday tranzaksiyalar topilmadi.")

# --- CALLBACK HANDLERS ---

@router.callback_query(F.data == "report_daily")
async def cb_report_daily(callback: CallbackQuery):
    await callback.answer("Bugungi hisobot tayyorlanmoqda...")
    text, chart_path = await report_service.generate_daily_report(callback.from_user.id)
    
    if chart_path and os.path.exists(chart_path):
        await callback.message.answer_photo(photo=FSInputFile(chart_path), caption=text)
    else:
        await callback.message.answer(text)
    await callback.message.delete()

@router.callback_query(F.data == "report_weekly")
async def cb_report_weekly(callback: CallbackQuery):
    await callback.answer("Haftalik hisobot tayyorlanmoqda...")
    text, chart_path = await report_service.generate_weekly_report(callback.from_user.id)
    
    if chart_path and os.path.exists(chart_path):
        await callback.message.answer_photo(photo=FSInputFile(chart_path), caption=text)
    else:
        await callback.message.answer(text)
    await callback.message.delete()

@router.callback_query(F.data == "report_monthly")
async def cb_report_monthly(callback: CallbackQuery):
    await callback.answer("Oylik hisobot tayyorlanmoqda...")
    text, chart_path = await report_service.generate_monthly_report(callback.from_user.id)
    
    if chart_path and os.path.exists(chart_path):
        await callback.message.answer_photo(photo=FSInputFile(chart_path), caption=text)
    else:
        await callback.message.answer(text)
    await callback.message.delete()

@router.callback_query(F.data == "report_ai")
async def cb_report_ai(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer("🤖 AI tahlil qilmoqda, iltimos kuting...")
    advice = await ai_service.get_financial_advice(callback.from_user.id)
    await callback.message.answer(advice)
    await callback.message.delete()

@router.callback_query(F.data == "report_excel")
async def cb_report_excel(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer("📤 Excel fayli tayyorlanmoqda...")
    end_date = date.today()
    start_date = end_date - timedelta(days=30)
    file_path = await report_service.export_to_excel(callback.from_user.id, start_date, end_date)
    
    if file_path and os.path.exists(file_path):
        await callback.message.answer_document(
            document=FSInputFile(file_path),
            caption=f"📊 Oxirgi 30 kunlik tranzaksiyalar hisoboti ({start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')})"
        )
    else:
        await callback.message.answer("❌ Ushbu davrda hech qanday tranzaksiyalar topilmadi.")
    await callback.message.delete()
