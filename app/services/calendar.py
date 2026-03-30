from collections import defaultdict
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.client import Client
from app.models.job import Job
from app.models.property import Property
from app.models.reminder import Reminder
from app.schemas.calendar import CalendarDay, CalendarEvent, CalendarResponse


async def get_calendar(
    db: AsyncSession, user_id: str, start: date, end: date
) -> CalendarResponse:
    # Jobs in range owned by user: Job -> Property -> Client.owner_id
    job_query = (
        select(Job)
        .join(Property, Job.property_id == Property.id)
        .join(Client, Property.client_id == Client.id)
        .where(
            Client.owner_id == user_id,
            Job.scheduled_date >= start,
            Job.scheduled_date <= end,
        )
    )
    job_result = await db.execute(job_query)
    jobs = job_result.scalars().all()

    # Reminders in range owned by user: Reminder -> Property -> Client.owner_id
    reminder_query = (
        select(Reminder)
        .join(Property, Reminder.property_id == Property.id)
        .join(Client, Property.client_id == Client.id)
        .where(
            Client.owner_id == user_id,
            Reminder.remind_date >= start,
            Reminder.remind_date <= end,
        )
    )
    reminder_result = await db.execute(reminder_query)
    reminders = reminder_result.scalars().all()

    # Convert to CalendarEvent and group by date
    events_by_date: dict[date, list[CalendarEvent]] = defaultdict(list)

    for job in jobs:
        events_by_date[job.scheduled_date].append(
            CalendarEvent(
                id=job.id,
                type="job",
                title=job.title,
                date=job.scheduled_date,
                status=job.status,
                job_type=job.job_type,
                property_id=job.property_id,
            )
        )

    for reminder in reminders:
        events_by_date[reminder.remind_date].append(
            CalendarEvent(
                id=reminder.id,
                type="reminder",
                title=reminder.title,
                date=reminder.remind_date,
                status=reminder.status,
                property_id=reminder.property_id,
                job_id=reminder.job_id,
            )
        )

    # Build sorted list of days
    days = [
        CalendarDay(date=d, events=events_by_date[d])
        for d in sorted(events_by_date.keys())
    ]

    total_events = sum(len(day.events) for day in days)

    return CalendarResponse(
        start=start,
        end=end,
        days=days,
        total_events=total_events,
    )
