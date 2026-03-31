from datetime import date, timedelta
from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.reminder import Reminder, ReminderStatus
from app.models.property import Property
from app.models.client import Client
from app.exceptions import NotFoundException

async def create_reminder(db: AsyncSession, owner_id: str, data: dict) -> Reminder:
    # Verify property ownership
    result = await db.execute(
        select(Property).join(Client).where(Property.id == data["property_id"], Client.owner_id == owner_id)
    )
    if not result.scalar_one_or_none():
        raise NotFoundException("Property not found")

    reminder = Reminder(**data)
    db.add(reminder)
    await db.commit()
    await db.refresh(reminder)
    return reminder

async def get_reminders(db: AsyncSession, owner_id: str, page: int = 1, size: int = 20, status: Optional[str] = None, search: Optional[str] = None) -> tuple[list[Reminder], int]:
    query = select(Reminder).join(Property).join(Client).where(Client.owner_id == owner_id)
    count_query = select(func.count()).select_from(Reminder).join(Property).join(Client).where(Client.owner_id == owner_id)

    if search:
        search_filter = f"%{search}%"
        search_cond = Reminder.title.ilike(search_filter) | Reminder.description.ilike(search_filter)
        query = query.where(search_cond)
        count_query = count_query.where(search_cond)
    if status:
        query = query.where(Reminder.status == status)
        count_query = count_query.where(Reminder.status == status)

    total_result = await db.execute(count_query)
    total = total_result.scalar()

    query = query.order_by(Reminder.remind_date.asc()).offset((page - 1) * size).limit(size)
    result = await db.execute(query)
    reminders = list(result.scalars().all())
    return reminders, total

async def get_upcoming_reminders(db: AsyncSession, owner_id: str, days: int = 30) -> list[Reminder]:
    today = date.today()
    end_date = today + timedelta(days=days)

    result = await db.execute(
        select(Reminder).join(Property).join(Client).where(
            Client.owner_id == owner_id,
            Reminder.status == ReminderStatus.PENDING,
            Reminder.remind_date >= today,
            Reminder.remind_date <= end_date,
        ).order_by(Reminder.remind_date.asc())
    )
    return list(result.scalars().all())

async def get_reminder(db: AsyncSession, owner_id: str, reminder_id: str) -> Reminder:
    result = await db.execute(
        select(Reminder).join(Property).join(Client).where(
            Reminder.id == reminder_id, Client.owner_id == owner_id
        )
    )
    reminder = result.scalar_one_or_none()
    if not reminder:
        raise NotFoundException("Reminder not found")
    return reminder

async def update_reminder(db: AsyncSession, owner_id: str, reminder_id: str, data: dict) -> Reminder:
    reminder = await get_reminder(db, owner_id, reminder_id)
    for key, value in data.items():
        if value is not None:
            setattr(reminder, key, value)
    await db.commit()
    await db.refresh(reminder)
    return reminder

async def delete_reminder(db: AsyncSession, owner_id: str, reminder_id: str) -> None:
    reminder = await get_reminder(db, owner_id, reminder_id)
    await db.delete(reminder)
    await db.commit()
