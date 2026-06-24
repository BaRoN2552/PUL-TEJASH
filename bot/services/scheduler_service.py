from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot
from sqlalchemy import select
from datetime import date
import logging
import os
from aiogram.types import FSInputFile

from bot.database import async_session_maker
from bot.models.user import User
from bot.services.report_service import report_service

logger = logging.getLogger(__name__)

async def send_daily_reports(bot: Bot):
    logger.info("Starting scheduled daily reports sending...")
    async with async_session_maker() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
        for u in users:
            try:
                text, chart_path = await report_service.generate_daily_report(u.id)
                if chart_path and os.path.exists(chart_path):
                    await bot.send_photo(chat_id=u.id, photo=FSInputFile(chart_path), caption=text)
                else:
                    await bot.send_message(chat_id=u.id, text=text)
            except Exception as e:
                logger.error(f"Error sending scheduled daily report to user {u.id}: {e}")

async def send_weekly_reports(bot: Bot):
    logger.info("Starting scheduled weekly reports sending...")
    async with async_session_maker() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
        for u in users:
            try:
                text, chart_path = await report_service.generate_weekly_report(u.id)
                if chart_path and os.path.exists(chart_path):
                    await bot.send_photo(chat_id=u.id, photo=FSInputFile(chart_path), caption=text)
                else:
                    await bot.send_message(chat_id=u.id, text=text)
            except Exception as e:
                logger.error(f"Error sending scheduled weekly report to user {u.id}: {e}")

async def send_monthly_reports(bot: Bot):
    logger.info("Starting scheduled monthly reports sending...")
    async with async_session_maker() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
        for u in users:
            try:
                text, chart_path = await report_service.generate_monthly_report(u.id)
                if chart_path and os.path.exists(chart_path):
                    await bot.send_photo(chat_id=u.id, photo=FSInputFile(chart_path), caption=text)
                else:
                    await bot.send_message(chat_id=u.id, text=text)
            except Exception as e:
                logger.error(f"Error sending scheduled monthly report to user {u.id}: {e}")

def setup_scheduler(bot: Bot) -> AsyncIOScheduler:
    """Configures the automatic reporting job queues."""
    scheduler = AsyncIOScheduler(timezone="Asia/Tashkent")
    
    # 21:00 daily auto-reports
    scheduler.add_job(send_daily_reports, "cron", hour=21, minute=0, args=[bot])
    
    # 09:00 Monday auto-reports
    scheduler.add_job(send_weekly_reports, "cron", day_of_week="mon", hour=9, minute=0, args=[bot])
    
    # 08:00 1st of month auto-reports
    scheduler.add_job(send_monthly_reports, "cron", day=1, hour=8, minute=0, args=[bot])
    
    scheduler.start()
    logger.info("APScheduler initialized for automatic daily/weekly/monthly reports.")
    return scheduler
