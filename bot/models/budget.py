from sqlalchemy import BigInteger, Integer, String, Boolean, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from bot.models.base import Base

class Budget(Base):
    __tablename__ = "budgets"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("categories.id", ondelete="CASCADE"))
    amount: Mapped[float] = mapped_column(Numeric(15, 2))
    period: Mapped[str] = mapped_column(String(10), default="monthly", server_default="monthly")  # monthly | weekly
    month: Mapped[int] = mapped_column(Integer, nullable=True)
    year: Mapped[int] = mapped_column(Integer, nullable=True)
    alert_80: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    alert_100: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")

    user = relationship("User", back_populates="budgets")
    category = relationship("Category", back_populates="budgets")
