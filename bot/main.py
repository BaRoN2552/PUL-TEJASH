import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import settings
from bot.database import init_db

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level, logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

async def main():
    logger.info("Initializing database...")
    await init_db()
    logger.info("Database initialized successfully.")

    # Initialize bot and dispatcher
    bot = Bot(token=settings.bot_token)
    dp = Dispatcher(storage=MemoryStorage())

    # Import routers
    from bot.handlers import (
        start, income, expense, quick, reports,
        budget, goals, debts, accounts, settings as settings_handler
    )

    # Register routers in logical order
    dp.include_router(start.router)
    dp.include_router(income.router)
    dp.include_router(expense.router)
    dp.include_router(quick.router)
    dp.include_router(reports.router)
    dp.include_router(budget.router)
    dp.include_router(goals.router)
    dp.include_router(debts.router)
    dp.include_router(accounts.router)
    dp.include_router(settings_handler.router)

    # Initialize scheduler for automated reports
    from bot.services.scheduler_service import setup_scheduler
    scheduler = setup_scheduler(bot)

    logger.info("Handlers registered. Starting polling...")
    try:
        # Delete webhook before polling to avoid conflicts
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped.")
