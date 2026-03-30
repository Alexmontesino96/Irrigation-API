from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.dependencies import get_current_user, CurrentUser
from app.schemas.property import PropertyCreate, PropertyUpdate, PropertyResponse
from app.schemas.common import PaginatedResponse
from app.services import property as property_service

router = APIRouter(prefix="/api/clients/{client_id}/properties", tags=["properties"])

@router.post("", response_model=PropertyResponse, status_code=201)
async def create_property(client_id: str, data: PropertyCreate, db: AsyncSession = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    return await property_service.create_property(db, current_user.id, client_id, data.model_dump())

@router.get("", response_model=PaginatedResponse[PropertyResponse])
async def list_properties(client_id: str, page: int = Query(1, ge=1), size: int = Query(20, ge=1, le=100), db: AsyncSession = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    properties, total = await property_service.get_properties(db, current_user.id, client_id, page, size)
    return PaginatedResponse(items=properties, total=total, page=page, size=size, pages=(total + size - 1) // size if total > 0 else 0)

@router.get("/{property_id}", response_model=PropertyResponse)
async def get_property(client_id: str, property_id: str, db: AsyncSession = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    return await property_service.get_property(db, current_user.id, property_id)

@router.patch("/{property_id}", response_model=PropertyResponse)
async def update_property(client_id: str, property_id: str, data: PropertyUpdate, db: AsyncSession = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    return await property_service.update_property(db, current_user.id, property_id, data.model_dump(exclude_unset=True))

@router.delete("/{property_id}", status_code=204)
async def delete_property(client_id: str, property_id: str, db: AsyncSession = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    await property_service.delete_property(db, current_user.id, property_id)
