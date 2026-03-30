from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user, CurrentUser
from app.schemas.calendar import CalendarResponse
from app.services.calendar import get_calendar

router = APIRouter(prefix="/api/calendar", tags=["calendar"])


@router.get("", response_model=CalendarResponse)
async def calendar(
    start: date = Query(..., description="Start date of the range"),
    end: date = Query(..., description="End date of the range"),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if end < start:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="end date must be >= start date",
        )
    delta = (end - start).days
    if delta > 366:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Date range cannot exceed 366 days",
        )
    return await get_calendar(db, current_user.id, start, end)
