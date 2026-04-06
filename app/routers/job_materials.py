from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.dependencies import get_current_user, CurrentUser
from app.schemas.job_material import JobMaterialCreate, JobMaterialUpdate, JobMaterialResponse
from app.services import job_material as job_material_service

router = APIRouter(prefix="/api/jobs/{job_id}/materials", tags=["job-materials"])


@router.post("", response_model=JobMaterialResponse, status_code=201)
async def add_material(
    job_id: str,
    data: JobMaterialCreate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    mat = await job_material_service.add_material(db, job_id, current_user.id, data.model_dump())
    return JobMaterialResponse.from_material(mat)


@router.get("", response_model=list[JobMaterialResponse])
async def list_materials(
    job_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    materials = await job_material_service.get_materials_by_job(db, job_id, current_user.id)
    return [JobMaterialResponse.from_material(m) for m in materials]


@router.patch("/{material_id}", response_model=JobMaterialResponse)
async def update_material(
    job_id: str,
    material_id: str,
    data: JobMaterialUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    mat = await job_material_service.update_material(db, material_id, current_user.id, data.model_dump(exclude_unset=True))
    return JobMaterialResponse.from_material(mat)


@router.delete("/{material_id}", status_code=204)
async def delete_material(
    job_id: str,
    material_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    await job_material_service.delete_material(db, material_id, current_user.id)
