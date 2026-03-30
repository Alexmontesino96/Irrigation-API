from fastapi import APIRouter, Depends, Query
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.dependencies import get_current_user, CurrentUser
from app.schemas.reminder import ReminderCreate, ReminderUpdate, ReminderResponse
from app.schemas.common import PaginatedResponse
from app.services import reminder as reminder_service

router = APIRouter(prefix="/api/reminders", tags=["reminders"])

@router.post("", response_model=ReminderResponse, status_code=201)
async def create_reminder(data: ReminderCreate, db: AsyncSession = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    return await reminder_service.create_reminder(db, current_user.id, data.model_dump())

@router.get("/upcoming", response_model=List[ReminderResponse])
async def upcoming_reminders(days: int = Query(30, ge=1, le=365), db: AsyncSession = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    return await reminder_service.get_upcoming_reminders(db, current_user.id, days)

@router.get("", response_model=PaginatedResponse[ReminderResponse])
async def list_reminders(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    reminders, total = await reminder_service.get_reminders(db, current_user.id, page, size, status)
    return PaginatedResponse(items=reminders, total=total, page=page, size=size, pages=(total + size - 1) // size if total > 0 else 0)

@router.get("/{reminder_id}", response_model=ReminderResponse)
async def get_reminder(reminder_id: str, db: AsyncSession = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    return await reminder_service.get_reminder(db, current_user.id, reminder_id)

@router.patch("/{reminder_id}", response_model=ReminderResponse)
async def update_reminder(reminder_id: str, data: ReminderUpdate, db: AsyncSession = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    return await reminder_service.update_reminder(db, current_user.id, reminder_id, data.model_dump(exclude_unset=True))

@router.delete("/{reminder_id}", status_code=204)
async def delete_reminder(reminder_id: str, db: AsyncSession = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    await reminder_service.delete_reminder(db, current_user.id, reminder_id)
