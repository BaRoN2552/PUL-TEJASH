from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, and_, or_
from datetime import date, datetime
from typing import List, Optional, Tuple, Dict, Any

from bot.database import async_session_maker
from bot.models.user import User
from bot.models.account import Account
from bot.models.category import Category
from bot.models.transaction import Transaction
from bot.models.budget import Budget
from bot.models.goal import Goal
from bot.models.debt import Debt
from bot.models.reminder import Reminder
from bot.services.currency_service import currency_service

class FinanceService:
    # --- USER SERVICES ---
    async def get_or_create_user(self, user_id: int, username: str = None, full_name: str = None) -> User:
        async with async_session_maker() as session:
            result = await session.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            if not user:
                user = User(
                    id=user_id,
                    username=username,
                    full_name=full_name,
                    language="uz",
                    currency="UZS",
                    timezone="Asia/Tashkent"
                )
                session.add(user)
                await session.commit()
                # Create a default "Naqd" (Cash) account for the new user
                await self.create_account(
                    user_id=user_id,
                    name="Naqd",
                    account_type="cash",
                    currency="UZS",
                    balance=0.0
                )
                # Refresh user reference
                result = await session.execute(select(User).where(User.id == user_id))
                user = result.scalar_one()
            else:
                user.last_active = datetime.now()
                await session.commit()
            return user

    async def update_user(self, user_id: int, **kwargs) -> Optional[User]:
        async with async_session_maker() as session:
            result = await session.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            if user:
                for key, value in kwargs.items():
                    if hasattr(user, key):
                        setattr(user, key, value)
                await session.commit()
                await session.refresh(user)
            return user

    # --- ACCOUNT SERVICES ---
    async def get_user_accounts(self, user_id: int) -> List[Account]:
        async with async_session_maker() as session:
            result = await session.execute(
                select(Account).where(Account.user_id == user_id, Account.is_active == True)
            )
            return list(result.scalars().all())

    async def get_account(self, account_id: int) -> Optional[Account]:
        async with async_session_maker() as session:
            result = await session.execute(select(Account).where(Account.id == account_id))
            return result.scalar_one_or_none()

    async def create_account(
        self, user_id: int, name: str, account_type: str, currency: str = "UZS",
        balance: float = 0.0, color: str = "#4CAF50", icon: str = "💰"
    ) -> Account:
        async with async_session_maker() as session:
            account = Account(
                user_id=user_id,
                name=name,
                type=account_type,
                currency=currency.upper(),
                balance=balance,
                color=color,
                icon=icon
            )
            session.add(account)
            await session.commit()
            await session.refresh(account)
            return account

    async def transfer_funds(self, user_id: int, from_acc_id: int, to_acc_id: int, amount: float) -> Tuple[bool, str]:
        """Transfer funds between accounts, handle currency conversion if different."""
        async with async_session_maker() as session:
            # Fetch accounts
            res_from = await session.execute(select(Account).where(Account.id == from_acc_id, Account.user_id == user_id))
            acc_from = res_from.scalar_one_or_none()
            res_to = await session.execute(select(Account).where(Account.id == to_acc_id, Account.user_id == user_id))
            acc_to = res_to.scalar_one_or_none()

            if not acc_from or not acc_to:
                return False, "Hisoblar topilmadi."

            if acc_from.balance < amount:
                return False, "Eski hisobda mablag' yetarli emas."

            # Calculate conversion
            converted_amount = await currency_service.convert(amount, acc_from.currency, acc_to.currency)

            # Update balances
            acc_from.balance -= amount
            acc_to.balance += converted_amount

            # Log transfer as transactions
            # Fetch or create a system "O'tkazma" Category
            result_cat = await session.execute(
                select(Category).where(Category.name == "O'tkazma", Category.user_id == user_id)
            )
            category = result_cat.scalar_one_or_none()
            if not category:
                category = Category(user_id=user_id, name="O'tkazma", type="expense", icon="🔄", color="#9E9E9E")
                session.add(category)
                await session.flush()

            amount_uzs = await currency_service.convert(amount, acc_from.currency, "UZS")

            tx_out = Transaction(
                user_id=user_id,
                account_id=from_acc_id,
                category_id=category.id,
                type="transfer",
                amount=amount,
                currency=acc_from.currency,
                amount_uzs=amount_uzs,
                description=f"{acc_to.name} hisobiga o'tkazma"
            )
            tx_in = Transaction(
                user_id=user_id,
                account_id=to_acc_id,
                category_id=category.id,
                type="transfer",
                amount=converted_amount,
                currency=acc_to.currency,
                amount_uzs=amount_uzs,
                description=f"{acc_from.name} hisobidan o'tkazma"
            )
            session.add_all([tx_out, tx_in])
            await session.commit()
            return True, "O'tkazma muvaffaqiyatli bajarildi."

    # --- CATEGORY SERVICES ---
    async def get_categories(self, user_id: int, cat_type: str = None) -> List[Category]:
        """Get categories: System defaults (user_id is Null) + Custom user categories."""
        async with async_session_maker() as session:
            conditions = [or_(Category.user_id == user_id, Category.user_id.is_(None))]
            if cat_type:
                conditions.append(Category.type == cat_type)
            
            result = await session.execute(
                select(Category).where(and_(*conditions)).order_by(Category.is_default.desc(), Category.name)
            )
            return list(result.scalars().all())

    async def get_category(self, category_id: int) -> Optional[Category]:
        async with async_session_maker() as session:
            result = await session.execute(select(Category).where(Category.id == category_id))
            return result.scalar_one_or_none()

    async def create_category(self, user_id: int, name: str, cat_type: str, icon: str = "📌", color: str = "#9E9E9E") -> Category:
        async with async_session_maker() as session:
            category = Category(
                user_id=user_id,
                name=name,
                type=cat_type,
                icon=icon,
                color=color,
                is_default=False
            )
            session.add(category)
            await session.commit()
            await session.refresh(category)
            return category

    # --- TRANSACTION SERVICES ---
    async def create_transaction(
        self, user_id: int, account_id: int, category_id: int, tx_type: str,
        amount: float, currency: str = "UZS", description: str = None, tx_date: date = None
    ) -> Tuple[Transaction, Dict[str, Any]]:
        """
        Create a transaction, update account balance, check budget limits.
        Returns the transaction and status dict (e.g. if budget exceeded).
        """
        async with async_session_maker() as session:
            # 1. Verify account
            result_acc = await session.execute(
                select(Account).where(Account.id == account_id, Account.user_id == user_id)
            )
            account = result_acc.scalar_one_or_none()
            if not account:
                raise ValueError("Hisob topilmadi.")

            # 2. Fetch conversion to UZS
            currency = currency.upper()
            amount_uzs = await currency_service.convert(amount, currency, "UZS")

            # 3. Update account balance
            if tx_type == "income":
                account.balance += amount
            elif tx_type == "expense":
                account.balance -= amount

            # 4. Save transaction
            tx = Transaction(
                user_id=user_id,
                account_id=account_id,
                category_id=category_id,
                type=tx_type,
                amount=amount,
                currency=currency,
                amount_uzs=amount_uzs,
                description=description,
                date=tx_date or date.today()
            )
            session.add(tx)
            await session.flush() # populate ID

            # 5. Check budget for expense
            budget_alert = {}
            if tx_type == "expense":
                # Find budget for this category and current month
                today = date.today()
                result_budget = await session.execute(
                    select(Budget).where(
                        Budget.user_id == user_id,
                        Budget.category_id == category_id,
                        Budget.month == today.month,
                        Budget.year == today.year
                    )
                )
                budget = result_budget.scalar_one_or_none()
                if budget:
                    # Calculate total spent in this category this month
                    start_of_month = date(today.year, today.month, 1)
                    # Sum all expense transaction amounts in UZS
                    sum_result = await session.execute(
                        select(func.sum(Transaction.amount_uzs)).where(
                            Transaction.user_id == user_id,
                            Transaction.category_id == category_id,
                            Transaction.type == "expense",
                            Transaction.date >= start_of_month,
                            Transaction.date <= today
                        )
                    )
                    total_spent_uzs = sum_result.scalar() or 0.0
                    
                    # Convert budget amount to UZS to compare
                    # Budgets are saved in base user currency or UZS, assume stored in user base currency.
                    # For simplicity, compare in UZS (assume budget amount is in UZS or user currency)
                    # We will assume budget amount is defined in UZS
                    budget_amount_uzs = float(budget.amount)
                    
                    percent = (total_spent_uzs / budget_amount_uzs) * 100
                    if percent >= 100:
                        budget_alert = {"status": "exceeded", "limit": budget_amount_uzs, "spent": total_spent_uzs, "percent": percent}
                    elif percent >= 80:
                        budget_alert = {"status": "warning", "limit": budget_amount_uzs, "spent": total_spent_uzs, "percent": percent}

            await session.commit()
            return tx, budget_alert

    async def get_transactions(
        self, user_id: int, start_date: date = None, end_date: date = None,
        tx_type: str = None, category_id: int = None, limit: int = 50
    ) -> List[Transaction]:
        async with async_session_maker() as session:
            query = select(Transaction).where(Transaction.user_id == user_id)
            if start_date:
                query = query.where(Transaction.date >= start_date)
            if end_date:
                query = query.where(Transaction.date <= end_date)
            if tx_type:
                query = query.where(Transaction.type == tx_type)
            if category_id:
                query = query.where(Transaction.category_id == category_id)
            
            query = query.order_by(Transaction.date.desc(), Transaction.id.desc()).limit(limit)
            result = await session.execute(query)
            return list(result.scalars().all())

    # --- BUDGET SERVICES ---
    async def set_budget(self, user_id: int, category_id: int, amount: float, period: str = "monthly") -> Budget:
        async with async_session_maker() as session:
            today = date.today()
            # Check if budget already exists
            result = await session.execute(
                select(Budget).where(
                    Budget.user_id == user_id,
                    Budget.category_id == category_id,
                    Budget.month == today.month,
                    Budget.year == today.year,
                    Budget.period == period
                )
            )
            budget = result.scalar_one_or_none()
            if budget:
                budget.amount = amount
            else:
                budget = Budget(
                    user_id=user_id,
                    category_id=category_id,
                    amount=amount,
                    period=period,
                    month=today.month,
                    year=today.year
                )
                session.add(budget)
            await session.commit()
            return budget

    async def get_budgets_status(self, user_id: int) -> List[Dict[str, Any]]:
        async with async_session_maker() as session:
            today = date.today()
            start_of_month = date(today.year, today.month, 1)

            # Get all budgets
            res_budgets = await session.execute(
                select(Budget).where(
                    Budget.user_id == user_id,
                    Budget.month == today.month,
                    Budget.year == today.year
                )
            )
            budgets = res_budgets.scalars().all()
            
            status_list = []
            for b in budgets:
                # Sum expenses for this category
                sum_res = await session.execute(
                    select(func.sum(Transaction.amount_uzs)).where(
                        Transaction.user_id == user_id,
                        Transaction.category_id == b.category_id,
                        Transaction.type == "expense",
                        Transaction.date >= start_of_month,
                        Transaction.date <= today
                    )
                )
                spent = sum_res.scalar() or 0.0
                
                # Fetch category name
                cat_res = await session.execute(select(Category).where(Category.id == b.category_id))
                cat = cat_res.scalar_one_or_none()
                cat_name = cat.name if cat else "Noma'lum"
                cat_icon = cat.icon if cat else "📌"
                
                status_list.append({
                    "category_id": b.category_id,
                    "category_name": cat_name,
                    "category_icon": cat_icon,
                    "limit": float(b.amount),
                    "spent": float(spent),
                    "percent": round((spent / float(b.amount)) * 100, 1) if b.amount > 0 else 0.0
                })
            return status_list

    # --- GOAL SERVICES ---
    async def create_goal(self, user_id: int, name: str, target_amount: float, currency: str = "UZS", deadline: date = None) -> Goal:
        async with async_session_maker() as session:
            goal = Goal(
                user_id=user_id,
                name=name,
                target_amount=target_amount,
                currency=currency.upper(),
                deadline=deadline
            )
            session.add(goal)
            await session.commit()
            await session.refresh(goal)
            return goal

    async def get_goals(self, user_id: int) -> List[Goal]:
        async with async_session_maker() as session:
            res = await session.execute(select(Goal).where(Goal.user_id == user_id))
            return list(res.scalars().all())

    async def add_savings_to_goal(self, user_id: int, goal_id: int, amount: float, account_id: int) -> Tuple[bool, str]:
        async with async_session_maker() as session:
            res_goal = await session.execute(select(Goal).where(Goal.id == goal_id, Goal.user_id == user_id))
            goal = res_goal.scalar_one_or_none()
            res_acc = await session.execute(select(Account).where(Account.id == account_id, Account.user_id == user_id))
            account = res_acc.scalar_one_or_none()

            if not goal or not account:
                return False, "Maqsad yoki hisob topilmadi."

            if account.balance < amount:
                return False, "Hisobingizda mablag' yetarli emas."

            # Calculate currency conversion (goal could be in USD, account in UZS or vice-versa)
            converted_amount = await currency_service.convert(amount, account.currency, goal.currency)

            # Update account balance and goal saved amount
            account.balance -= amount
            goal.current_amount += converted_amount

            if goal.current_amount >= goal.target_amount:
                goal.is_achieved = True

            # Save as transaction
            result_cat = await session.execute(
                select(Category).where(Category.name == "Jamg'arma", Category.user_id == user_id)
            )
            category = result_cat.scalar_one_or_none()
            if not category:
                category = Category(user_id=user_id, name="Jamg'arma", type="expense", icon="🎯", color="#E91E63")
                session.add(category)
                await session.flush()

            amount_uzs = await currency_service.convert(amount, account.currency, "UZS")

            tx = Transaction(
                user_id=user_id,
                account_id=account_id,
                category_id=category.id,
                type="expense",
                amount=amount,
                currency=account.currency,
                amount_uzs=amount_uzs,
                description=f"'{goal.name}' maqsadiga jamg'arish"
            )
            session.add(tx)
            await session.commit()
            return True, f"'{goal.name}' maqsadiga {amount} {account.currency} o'tkazildi!"

    # --- DEBT SERVICES ---
    async def create_debt(
        self, user_id: int, person_name: str, amount: float, currency: str,
        debt_type: str, description: str = None, due_date: date = None
    ) -> Debt:
        async with async_session_maker() as session:
            debt = Debt(
                user_id=user_id,
                person_name=person_name,
                amount=amount,
                currency=currency.upper(),
                type=debt_type,  # given | received
                description=description,
                due_date=due_date
            )
            session.add(debt)
            await session.commit()
            await session.refresh(debt)
            return debt

    async def get_debts(self, user_id: int, is_settled: bool = False) -> List[Debt]:
        async with async_session_maker() as session:
            res = await session.execute(
                select(Debt).where(Debt.user_id == user_id, Debt.is_settled == is_settled)
            )
            return list(res.scalars().all())

    async def settle_debt(self, user_id: int, debt_id: int, account_id: Optional[int] = None) -> Tuple[bool, str]:
        """Settle a debt, optionally adjust account balance."""
        async with async_session_maker() as session:
            res = await session.execute(select(Debt).where(Debt.id == debt_id, Debt.user_id == user_id))
            debt = res.scalar_one_or_none()
            if not debt:
                return False, "Qarz topilmadi."

            if debt.is_settled:
                return False, "Qarz allaqachon yopilgan."

            if account_id:
                res_acc = await session.execute(select(Account).where(Account.id == account_id, Account.user_id == user_id))
                account = res_acc.scalar_one_or_none()
                if not account:
                    return False, "Hisob topilmadi."

                # Convert debt amount to account currency
                converted_amount = await currency_service.convert(debt.amount, debt.currency, account.currency)
                
                # If we received debt earlier, we pay it back now (expense)
                # If we gave debt earlier, we receive it back now (income)
                if debt.type == "received":
                    if account.balance < converted_amount:
                        return False, "Hisobda yetarli mablag' yo'q."
                    account.balance -= converted_amount
                    tx_type = "expense"
                else:
                    account.balance += converted_amount
                    tx_type = "income"

                # Log transaction
                result_cat = await session.execute(
                    select(Category).where(Category.name == "Qarz", Category.user_id == user_id)
                )
                category = result_cat.scalar_one_or_none()
                if not category:
                    category = Category(user_id=user_id, name="Qarz", type="expense" if tx_type == "expense" else "income", icon="🤝", color="#FF9800")
                    session.add(category)
                    await session.flush()

                amount_uzs = await currency_service.convert(converted_amount, account.currency, "UZS")
                
                tx = Transaction(
                    user_id=user_id,
                    account_id=account_id,
                    category_id=category.id,
                    type=tx_type,
                    amount=converted_amount,
                    currency=account.currency,
                    amount_uzs=amount_uzs,
                    description=f"{debt.person_name} bilan qarz yopildi"
                )
                session.add(tx)

            debt.is_settled = True
            await session.commit()
            return True, "Qarz muvaffaqiyatli yopildi."

finance_service = FinanceService()
