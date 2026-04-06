from datetime import date, timedelta
from typing import Optional
from sqlalchemy import select, func, extract, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.invoice import Invoice, InvoiceStatus
from app.models.expense import Expense
from app.models.job import Job, JobStatus
from app.models.property import Property
from app.models.client import Client


async def get_financial_summary(db: AsyncSession, owner_id: str) -> dict:
    today = date.today()
    first_this_month = today.replace(day=1)
    first_last_month = (first_this_month - timedelta(days=1)).replace(day=1)

    # Revenue this month
    result = await db.execute(
        select(func.coalesce(func.sum(Invoice.total), 0)).where(
            Invoice.owner_id == owner_id,
            Invoice.status == InvoiceStatus.PAID.value,
            Invoice.paid_date >= first_this_month,
            Invoice.paid_date <= today,
        )
    )
    revenue_this_month = float(result.scalar())

    # Revenue last month
    result = await db.execute(
        select(func.coalesce(func.sum(Invoice.total), 0)).where(
            Invoice.owner_id == owner_id,
            Invoice.status == InvoiceStatus.PAID.value,
            Invoice.paid_date >= first_last_month,
            Invoice.paid_date < first_this_month,
        )
    )
    revenue_last_month = float(result.scalar())

    # Revenue change %
    if revenue_last_month > 0:
        revenue_change_pct = round(((revenue_this_month - revenue_last_month) / revenue_last_month) * 100, 1)
    else:
        revenue_change_pct = 100.0 if revenue_this_month > 0 else 0.0

    # Expenses this month
    result = await db.execute(
        select(func.coalesce(func.sum(Expense.amount), 0)).where(
            Expense.owner_id == owner_id,
            Expense.expense_date >= first_this_month,
            Expense.expense_date <= today,
        )
    )
    expenses_this_month = float(result.scalar())

    # Outstanding
    result = await db.execute(
        select(func.coalesce(func.sum(Invoice.total), 0)).where(
            Invoice.owner_id == owner_id,
            Invoice.status.in_([InvoiceStatus.SENT.value, InvoiceStatus.OVERDUE.value]),
        )
    )
    outstanding = float(result.scalar())

    # Jobs completed this month
    result = await db.execute(
        select(func.count()).select_from(Job).join(Property).join(Client).where(
            Client.owner_id == owner_id,
            Job.status == JobStatus.COMPLETED.value,
            Job.completed_date >= first_this_month,
            Job.completed_date <= today,
        )
    )
    jobs_completed = result.scalar()

    return {
        "revenue_this_month": revenue_this_month,
        "revenue_last_month": revenue_last_month,
        "revenue_change_pct": revenue_change_pct,
        "expenses_this_month": expenses_this_month,
        "profit_margin": round(revenue_this_month - expenses_this_month, 2),
        "outstanding": outstanding,
        "jobs_completed": jobs_completed,
    }


async def get_monthly_revenue(db: AsyncSession, owner_id: str, months: int = 12) -> list[dict]:
    today = date.today()
    data = []

    for i in range(months - 1, -1, -1):
        # Calculate month start/end
        month_date = today.replace(day=1) - timedelta(days=i * 30)
        month_date = month_date.replace(day=1)
        if month_date.month == 12:
            next_month = month_date.replace(year=month_date.year + 1, month=1)
        else:
            next_month = month_date.replace(month=month_date.month + 1)

        # Revenue
        result = await db.execute(
            select(func.coalesce(func.sum(Invoice.total), 0)).where(
                Invoice.owner_id == owner_id,
                Invoice.status == InvoiceStatus.PAID.value,
                Invoice.paid_date >= month_date,
                Invoice.paid_date < next_month,
            )
        )
        revenue = float(result.scalar())

        # Expenses
        result = await db.execute(
            select(func.coalesce(func.sum(Expense.amount), 0)).where(
                Expense.owner_id == owner_id,
                Expense.expense_date >= month_date,
                Expense.expense_date < next_month,
            )
        )
        expenses = float(result.scalar())

        data.append({
            "month": month_date.strftime("%Y-%m"),
            "revenue": revenue,
            "expenses": expenses,
        })

    return data


async def get_revenue_by_type(
    db: AsyncSession,
    owner_id: str,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
) -> list[dict]:
    # This is simplified - joins invoices to jobs via invoice_items
    query = (
        select(
            Job.job_type,
            func.coalesce(func.sum(Job.price), 0).label("total"),
            func.count().label("count"),
        )
        .join(Property)
        .join(Client)
        .where(
            Client.owner_id == owner_id,
            Job.status == JobStatus.COMPLETED.value,
        )
        .group_by(Job.job_type)
    )
    if date_from:
        query = query.where(Job.completed_date >= date_from)
    if date_to:
        query = query.where(Job.completed_date <= date_to)

    result = await db.execute(query)
    rows = result.all()
    return [{"job_type": r.job_type, "total": float(r.total or 0), "count": r.count} for r in rows]
