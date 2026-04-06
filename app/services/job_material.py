from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.job_material import JobMaterial
from app.models.job import Job
from app.models.property import Property
from app.models.client import Client
from app.exceptions import NotFoundException


async def _verify_job_ownership(db: AsyncSession, job_id: str, owner_id: str) -> Job:
    result = await db.execute(
        select(Job).join(Property).join(Client).where(
            Job.id == job_id, Client.owner_id == owner_id
        )
    )
    job = result.scalar_one_or_none()
    if not job:
        raise NotFoundException("Job not found")
    return job


async def _verify_material_ownership(db: AsyncSession, material_id: str, owner_id: str) -> JobMaterial:
    result = await db.execute(
        select(JobMaterial).join(Job).join(Property).join(Client).where(
            JobMaterial.id == material_id, Client.owner_id == owner_id
        )
    )
    mat = result.scalar_one_or_none()
    if not mat:
        raise NotFoundException("Material not found")
    return mat


async def add_material(db: AsyncSession, job_id: str, owner_id: str, data: dict) -> JobMaterial:
    await _verify_job_ownership(db, job_id, owner_id)
    mat = JobMaterial(job_id=job_id, **data)
    db.add(mat)
    await db.commit()
    await db.refresh(mat)
    return mat


async def get_materials_by_job(db: AsyncSession, job_id: str, owner_id: str) -> list[JobMaterial]:
    await _verify_job_ownership(db, job_id, owner_id)
    result = await db.execute(
        select(JobMaterial).where(JobMaterial.job_id == job_id).order_by(JobMaterial.created_at)
    )
    return list(result.scalars().all())


async def update_material(db: AsyncSession, material_id: str, owner_id: str, data: dict) -> JobMaterial:
    mat = await _verify_material_ownership(db, material_id, owner_id)
    for key, value in data.items():
        if value is not None:
            setattr(mat, key, value)
    await db.commit()
    await db.refresh(mat)
    return mat


async def delete_material(db: AsyncSession, material_id: str, owner_id: str) -> None:
    mat = await _verify_material_ownership(db, material_id, owner_id)
    await db.delete(mat)
    await db.commit()
