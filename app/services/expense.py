from datetime import date
from typing import Optional
from sqlalchemy import select, func, asc, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.expense import Expense
from app.exceptions import NotFoundException

_EXPENSE_SORT_WHITELIST = {"expense_date", "amount", "category", "created_at"}


async def create_expense(db: AsyncSession, owner_id: str, data: dict) -> Expense:
    expense = Expense(owner_id=owner_id, **data)
    db.add(expense)
    await db.commit()
    await db.refresh(expense)
    return expense


async def get_expenses(
    db: AsyncSession,
    owner_id: str,
    page: int = 1,
    size: int = 20,
    category: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    sort_by: str = "expense_date",
    sort_order: str = "desc",
) -> tuple[list[Expense], int]:
    query = select(Expense).where(Expense.owner_id == owner_id)
    count_query = select(func.count()).select_from(Expense).where(Expense.owner_id == owner_id)

    if category:
        query = query.where(Expense.category == category)
        count_query = count_query.where(Expense.category == category)
    if date_from:
        query = query.where(Expense.expense_date >= date_from)
        count_query = count_query.where(Expense.expense_date >= date_from)
    if date_to:
        query = query.where(Expense.expense_date <= date_to)
        count_query = count_query.where(Expense.expense_date <= date_to)

    total_result = await db.execute(count_query)
    total = total_result.scalar()

    col = getattr(Expense, sort_by) if sort_by in _EXPENSE_SORT_WHITELIST else Expense.expense_date
    order_fn = asc if sort_order == "asc" else desc
    query = query.order_by(order_fn(col)).offset((page - 1) * size).limit(size)

    result = await db.execute(query)
    expenses = list(result.scalars().all())
    return expenses, total


async def get_expense(db: AsyncSession, expense_id: str, owner_id: str) -> Expense:
    result = await db.execute(
        select(Expense).where(Expense.id == expense_id, Expense.owner_id == owner_id)
    )
    expense = result.scalar_one_or_none()
    if not expense:
        raise NotFoundException("Expense not found")
    return expense


async def update_expense(db: AsyncSession, expense_id: str, owner_id: str, data: dict) -> Expense:
    expense = await get_expense(db, expense_id, owner_id)
    for key, value in data.items():
        if value is not None:
            setattr(expense, key, value)
    await db.commit()
    await db.refresh(expense)
    return expense


async def delete_expense(db: AsyncSession, expense_id: str, owner_id: str) -> None:
    expense = await get_expense(db, expense_id, owner_id)
    await db.delete(expense)
    await db.commit()


async def get_expense_summary(
    db: AsyncSession,
    owner_id: str,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
) -> list[dict]:
    query = (
        select(
            Expense.category,
            func.sum(Expense.amount).label("total"),
            func.count().label("count"),
        )
        .where(Expense.owner_id == owner_id)
        .group_by(Expense.category)
    )
    if date_from:
        query = query.where(Expense.expense_date >= date_from)
    if date_to:
        query = query.where(Expense.expense_date <= date_to)

    result = await db.execute(query)
    rows = result.all()
    return [{"category": r.category, "total": float(r.total or 0), "count": r.count} for r in rows]
