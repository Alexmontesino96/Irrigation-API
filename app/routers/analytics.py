from datetime import date
from fastapi import APIRouter, Depends, Query
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.dependencies import get_current_user, CurrentUser
from app.schemas.analytics import FinancialSummary, MonthlyData, RevenueByType
from app.services import analytics as analytics_service

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/financial-summary", response_model=FinancialSummary)
async def financial_summary(
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    return await analytics_service.get_financial_summary(db, current_user.id)


@router.get("/monthly-revenue", response_model=list[MonthlyData])
async def monthly_revenue(
    months: int = Query(12, ge=1, le=24),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    return await analytics_service.get_monthly_revenue(db, current_user.id, months)


@router.get("/revenue-by-type", response_model=list[RevenueByType])
async def revenue_by_type(
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    return await analytics_service.get_revenue_by_type(db, current_user.id, date_from, date_to)
