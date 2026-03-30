from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.dependencies import get_current_user, CurrentUser
from app.schemas.job_note import JobNoteCreate, JobNoteUpdate, JobNoteResponse
from app.schemas.common import PaginatedResponse
from app.services import job_note as note_service

router = APIRouter(prefix="/api/jobs/{job_id}/notes", tags=["job_notes"])

@router.post("", response_model=JobNoteResponse, status_code=201)
async def create_note(job_id: str, data: JobNoteCreate, db: AsyncSession = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    return await note_service.create_job_note(db, current_user.id, job_id, data.content)

@router.get("", response_model=PaginatedResponse[JobNoteResponse])
async def list_notes(job_id: str, page: int = Query(1, ge=1), size: int = Query(20, ge=1, le=100), db: AsyncSession = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    notes, total = await note_service.get_job_notes(db, current_user.id, job_id, page, size)
    return PaginatedResponse(items=notes, total=total, page=page, size=size, pages=(total + size - 1) // size if total > 0 else 0)

@router.get("/{note_id}", response_model=JobNoteResponse)
async def get_note(job_id: str, note_id: str, db: AsyncSession = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    return await note_service.get_job_note(db, current_user.id, note_id)

@router.patch("/{note_id}", response_model=JobNoteResponse)
async def update_note(job_id: str, note_id: str, data: JobNoteUpdate, db: AsyncSession = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    return await note_service.update_job_note(db, current_user.id, note_id, data.content)

@router.delete("/{note_id}", status_code=204)
async def delete_note(job_id: str, note_id: str, db: AsyncSession = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    await note_service.delete_job_note(db, current_user.id, note_id)
