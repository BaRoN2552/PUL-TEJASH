from sqlalchemy import BigInteger, String, Boolean, DateTime, Date, Numeric, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date, datetime
from bot.models.base import Base

class Goal(Base):
    __tablename__ = "goals"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(200))
    target_amount: Mapped[float] = mapped_column(Numeric(15, 2))
    current_amount: Mapped[float] = mapped_column(Numeric(15, 2), default=0.00, server_default="0.00")
    currency: Mapped[str] = mapped_column(String(3), default="UZS", server_default="UZS")
    deadline: Mapped[date] = mapped_column(Date, nullable=True)
    is_achieved: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), server_default=func.now())

    user = relationship("User", back_populates="goals")
