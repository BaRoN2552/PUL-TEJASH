from sqlalchemy import BigInteger, String, Boolean, DateTime, Numeric, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from bot.models.base import Base

class Reminder(Base):
    __tablename__ = "reminders"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(200))
    amount: Mapped[float] = mapped_column(Numeric(15, 2), nullable=True)
    schedule: Mapped[str] = mapped_column(String(50))  # monthly:25 | weekly:1
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    last_sent: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), server_default=func.now())

    user = relationship("User", back_populates="reminders")
