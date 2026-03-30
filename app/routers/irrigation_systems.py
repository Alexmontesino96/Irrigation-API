from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.dependencies import get_current_user, CurrentUser
from app.schemas.irrigation_system import IrrigationSystemCreate, IrrigationSystemUpdate, IrrigationSystemResponse
from app.schemas.common import PaginatedResponse
from app.services import irrigation_system as system_service

router = APIRouter(prefix="/api/properties/{property_id}/systems", tags=["irrigation_systems"])

@router.post("", response_model=IrrigationSystemResponse, status_code=201)
async def create_system(property_id: str, data: IrrigationSystemCreate, db: AsyncSession = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    return await system_service.create_irrigation_system(db, current_user.id, property_id, data.model_dump())

@router.get("", response_model=PaginatedResponse[IrrigationSystemResponse])
async def list_systems(property_id: str, page: int = Query(1, ge=1), size: int = Query(20, ge=1, le=100), db: AsyncSession = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    systems, total = await system_service.get_irrigation_systems(db, current_user.id, property_id, page, size)
    return PaginatedResponse(items=systems, total=total, page=page, size=size, pages=(total + size - 1) // size if total > 0 else 0)

@router.get("/{system_id}", response_model=IrrigationSystemResponse)
async def get_system(property_id: str, system_id: str, db: AsyncSession = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    return await system_service.get_irrigation_system(db, current_user.id, system_id)

@router.patch("/{system_id}", response_model=IrrigationSystemResponse)
async def update_system(property_id: str, system_id: str, data: IrrigationSystemUpdate, db: AsyncSession = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    return await system_service.update_irrigation_system(db, current_user.id, system_id, data.model_dump(exclude_unset=True))

@router.delete("/{system_id}", status_code=204)
async def delete_system(property_id: str, system_id: str, db: AsyncSession = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    await system_service.delete_irrigation_system(db, current_user.id, system_id)
