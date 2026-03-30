from datetime import date, timedelta
from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.job import Job, JobStatus, JobType
from app.models.reminder import Reminder, ReminderStatus
from app.models.property import Property
from app.models.client import Client
from app.exceptions import NotFoundException

async def _verify_property_ownership(db: AsyncSession, property_id: str, owner_id: str) -> Property:
    result = await db.execute(
        select(Property).join(Client).where(Property.id == property_id, Client.owner_id == owner_id)
    )
    prop = result.scalar_one_or_none()
    if not prop:
        raise NotFoundException("Property not found")
    return prop

async def create_job(db: AsyncSession, owner_id: str, data: dict) -> Job:
    await _verify_property_ownership(db, data["property_id"], owner_id)
    job = Job(**data)
    db.add(job)
    await db.commit()
    await db.refresh(job)
    return job

async def get_jobs(db: AsyncSession, owner_id: str, page: int = 1, size: int = 20, status: Optional[str] = None, job_type: Optional[str] = None, property_id: Optional[str] = None) -> tuple[list[Job], int]:
    query = select(Job).join(Property).join(Client).where(Client.owner_id == owner_id)
    count_query = select(func.count()).select_from(Job).join(Property).join(Client).where(Client.owner_id == owner_id)

    if status:
        query = query.where(Job.status == status)
        count_query = count_query.where(Job.status == status)
    if job_type:
        query = query.where(Job.job_type == job_type)
        count_query = count_query.where(Job.job_type == job_type)
    if property_id:
        query = query.where(Job.property_id == property_id)
        count_query = count_query.where(Job.property_id == property_id)

    total_result = await db.execute(count_query)
    total = total_result.scalar()

    query = query.order_by(Job.scheduled_date.desc()).offset((page - 1) * size).limit(size)
    result = await db.execute(query)
    jobs = list(result.scalars().all())
    return jobs, total

async def get_job(db: AsyncSession, owner_id: str, job_id: str) -> Job:
    result = await db.execute(
        select(Job).join(Property).join(Client).where(Job.id == job_id, Client.owner_id == owner_id)
    )
    job = result.scalar_one_or_none()
    if not job:
        raise NotFoundException("Job not found")
    return job

async def update_job(db: AsyncSession, owner_id: str, job_id: str, data: dict) -> Job:
    job = await get_job(db, owner_id, job_id)
    old_status = job.status

    for key, value in data.items():
        if value is not None:
            setattr(job, key, value)

    # Auto-generate reminders when job is completed and has reminder_days
    new_status = data.get("status")
    if (new_status == JobStatus.COMPLETED and old_status != JobStatus.COMPLETED
            and job.reminder_days):
        base_date = job.completed_date or date.today()
        for days in job.reminder_days:
            reminder = Reminder(
                job_id=job.id,
                property_id=job.property_id,
                title=f"Follow-up ({days} days) - {job.title}",
                description=f"Auto-generated reminder for follow-up from job: {job.title}",
                remind_date=base_date + timedelta(days=days),
                status=ReminderStatus.PENDING,
                is_auto_generated=True,
            )
            db.add(reminder)

    await db.commit()
    await db.refresh(job)
    return job

async def delete_job(db: AsyncSession, owner_id: str, job_id: str) -> None:
    job = await get_job(db, owner_id, job_id)
    await db.delete(job)
    await db.commit()
