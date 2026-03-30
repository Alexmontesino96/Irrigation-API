from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.job_note import JobNote
from app.models.job import Job
from app.models.property import Property
from app.models.client import Client
from app.exceptions import NotFoundException

async def _verify_job_ownership(db: AsyncSession, job_id: str, owner_id: str) -> Job:
    result = await db.execute(
        select(Job).join(Property).join(Client).where(Job.id == job_id, Client.owner_id == owner_id)
    )
    job = result.scalar_one_or_none()
    if not job:
        raise NotFoundException("Job not found")
    return job

async def create_job_note(db: AsyncSession, owner_id: str, job_id: str, content: str) -> JobNote:
    await _verify_job_ownership(db, job_id, owner_id)
    note = JobNote(job_id=job_id, content=content)
    db.add(note)
    await db.commit()
    await db.refresh(note)
    return note

async def get_job_notes(db: AsyncSession, owner_id: str, job_id: str, page: int = 1, size: int = 20) -> tuple[list[JobNote], int]:
    await _verify_job_ownership(db, job_id, owner_id)

    count_query = select(func.count()).select_from(JobNote).where(JobNote.job_id == job_id)
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    query = select(JobNote).where(JobNote.job_id == job_id).order_by(JobNote.created_at.desc()).offset((page - 1) * size).limit(size)
    result = await db.execute(query)
    notes = list(result.scalars().all())
    return notes, total

async def get_job_note(db: AsyncSession, owner_id: str, note_id: str) -> JobNote:
    result = await db.execute(
        select(JobNote).join(Job).join(Property).join(Client).where(
            JobNote.id == note_id, Client.owner_id == owner_id
        )
    )
    note = result.scalar_one_or_none()
    if not note:
        raise NotFoundException("Job note not found")
    return note

async def update_job_note(db: AsyncSession, owner_id: str, note_id: str, content: str) -> JobNote:
    note = await get_job_note(db, owner_id, note_id)
    note.content = content
    await db.commit()
    await db.refresh(note)
    return note

async def delete_job_note(db: AsyncSession, owner_id: str, note_id: str) -> None:
    note = await get_job_note(db, owner_id, note_id)
    await db.delete(note)
    await db.commit()
