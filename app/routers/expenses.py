from datetime import date
from fastapi import APIRouter, Depends, Query
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.dependencies import get_current_user, CurrentUser
from app.schemas.expense import ExpenseCreate, ExpenseUpdate, ExpenseResponse, ExpenseSummary
from app.schemas.common import PaginatedResponse
from app.services import expense as expense_service

router = APIRouter(prefix="/api/expenses", tags=["expenses"])


@router.post("", response_model=ExpenseResponse, status_code=201)
async def create_expense(
    data: ExpenseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    return await expense_service.create_expense(db, current_user.id, data.model_dump())


@router.get("", response_model=PaginatedResponse[ExpenseResponse])
async def list_expenses(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    expenses, total = await expense_service.get_expenses(
        db, current_user.id, page, size, category, date_from, date_to,
        sort_by=sort_by or "expense_date", sort_order=sort_order or "desc"
    )
    return PaginatedResponse(
        items=expenses, total=total, page=page, size=size,
        pages=(total + size - 1) // size if total > 0 else 0
    )


@router.get("/summary", response_model=list[ExpenseSummary])
async def expense_summary(
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    return await expense_service.get_expense_summary(db, current_user.id, date_from, date_to)


@router.get("/{expense_id}", response_model=ExpenseResponse)
async def get_expense(
    expense_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    return await expense_service.get_expense(db, expense_id, current_user.id)


@router.patch("/{expense_id}", response_model=ExpenseResponse)
async def update_expense(
    expense_id: str,
    data: ExpenseUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    return await expense_service.update_expense(db, expense_id, current_user.id, data.model_dump(exclude_unset=True))


@router.delete("/{expense_id}", status_code=204)
async def delete_expense(
    expense_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    await expense_service.delete_expense(db, expense_id, current_user.id)
