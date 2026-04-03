from fastapi import APIRouter, Depends, Query
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.dependencies import get_current_user, CurrentUser
from app.schemas.job import JobCreate, JobUpdate, JobResponse
from app.schemas.common import PaginatedResponse
from app.services import job as job_service

router = APIRouter(prefix="/api/jobs", tags=["jobs"])

@router.post("", response_model=JobResponse, status_code=201)
async def create_job(data: JobCreate, db: AsyncSession = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    return await job_service.create_job(db, current_user.id, data.model_dump())

@router.get("", response_model=PaginatedResponse[JobResponse])
async def list_jobs(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    job_type: Optional[str] = None,
    property_id: Optional[str] = None,
    overdue: Optional[bool] = None,
    search: Optional[str] = None,
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    jobs, total = await job_service.get_jobs(db, current_user.id, page, size, status, job_type, property_id, overdue, search, sort_by=sort_by or "scheduled_date", sort_order=sort_order or "desc")
    items = [JobResponse.from_job(j) for j in jobs]
    return PaginatedResponse(items=items, total=total, page=page, size=size, pages=(total + size - 1) // size if total > 0 else 0)

@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: str, db: AsyncSession = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    job = await job_service.get_job(db, current_user.id, job_id)
    return JobResponse.from_job(job)

@router.patch("/{job_id}", response_model=JobResponse)
async def update_job(job_id: str, data: JobUpdate, db: AsyncSession = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    return await job_service.update_job(db, current_user.id, job_id, data.model_dump(exclude_unset=True))

@router.delete("/{job_id}", status_code=204)
async def delete_job(job_id: str, db: AsyncSession = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    await job_service.delete_job(db, current_user.id, job_id)
