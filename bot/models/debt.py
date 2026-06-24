from sqlalchemy import BigInteger, String, Boolean, DateTime, Date, Numeric, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date, datetime
from bot.models.base import Base

class Debt(Base):
    __tablename__ = "debts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))
    person_name: Mapped[str] = mapped_column(String(100))
    amount: Mapped[float] = mapped_column(Numeric(15, 2))
    currency: Mapped[str] = mapped_column(String(3), default="UZS", server_default="UZS")
    type: Mapped[str] = mapped_column(String(10))  # given | received
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    due_date: Mapped[date] = mapped_column(Date, nullable=True)
    is_settled: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    date: Mapped[date] = mapped_column(Date, default=func.current_date(), server_default=func.current_date())
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), server_default=func.now())

    user = relationship("User", back_populates="debts")
