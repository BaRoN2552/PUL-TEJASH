from sqlalchemy import BigInteger, Integer, String, Boolean, DateTime, Date, Numeric, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date, datetime
from bot.models.base import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))
    account_id: Mapped[int] = mapped_column(Integer, ForeignKey("accounts.id", ondelete="CASCADE"), nullable=True)
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    type: Mapped[str] = mapped_column(String(10))  # income | expense | transfer
    amount: Mapped[float] = mapped_column(Numeric(15, 2))
    currency: Mapped[str] = mapped_column(String(3), default="UZS", server_default="UZS")
    amount_uzs: Mapped[float] = mapped_column(Numeric(15, 2))
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    date: Mapped[date] = mapped_column(Date, default=func.current_date(), server_default=func.current_date())
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), server_default=func.now())
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    recurring_id: Mapped[int] = mapped_column(Integer, nullable=True)

    user = relationship("User", back_populates="transactions")
    account = relationship("Account", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")
