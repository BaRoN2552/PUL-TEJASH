from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from bot.config import settings
from bot.models.base import Base
from sqlalchemy import select

DATABASE_URL = settings.database_url

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_async_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=False
)

async_session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def init_db():
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Populate default categories
    from bot.models.category import Category
    
    default_categories = [
        # Incomes
        {"name": "Maosh", "type": "income", "icon": "💰", "color": "#4CAF50", "is_default": True},
        {"name": "Qo'shimcha daromad", "type": "income", "icon": "💸", "color": "#8BC34A", "is_default": True},
        {"name": "Sovg'a", "type": "income", "icon": "🎁", "color": "#CDDC39", "is_default": True},
        # Expenses
        {"name": "Oziq-ovqat", "type": "expense", "icon": "🍞", "color": "#FF5722", "is_default": True},
        {"name": "Transport", "type": "expense", "icon": "🚗", "color": "#03A9F4", "is_default": True},
        {"name": "Ijara", "type": "expense", "icon": "🏠", "color": "#9C27B0", "is_default": True},
        {"name": "Sog'liq", "type": "expense", "icon": "💊", "color": "#E91E63", "is_default": True},
        {"name": "Ko'ngilochar", "type": "expense", "icon": "🎮", "color": "#9E9E9E", "is_default": True},
        {"name": "Kafe", "type": "expense", "icon": "☕", "color": "#795548", "is_default": True},
        {"name": "Xarid", "type": "expense", "icon": "🛒", "color": "#FFC107", "is_default": True},
        {"name": "Kommunal", "type": "expense", "icon": "⚡", "color": "#FF9800", "is_default": True},
    ]
    
    async with async_session_maker() as session:
        for cat_data in default_categories:
            result = await session.execute(
                select(Category).where(
                    Category.name == cat_data["name"],
                    Category.type == cat_data["type"],
                    Category.user_id.is_(None)
                )
            )
            existing = result.scalar_one_or_none()
            if not existing:
                cat = Category(
                    name=cat_data["name"],
                    type=cat_data["type"],
                    icon=cat_data["icon"],
                    color=cat_data["color"],
                    is_default=cat_data["is_default"]
                )
                session.add(cat)
        await session.commit()
