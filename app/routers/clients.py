from fastapi import APIRouter, Depends, Query
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.dependencies import get_current_user, CurrentUser
from app.schemas.client import ClientCreate, ClientUpdate, ClientResponse
from app.schemas.common import PaginatedResponse
from app.services import client as client_service

router = APIRouter(prefix="/api/clients", tags=["clients"])

@router.post("", response_model=ClientResponse, status_code=201)
async def create_client(data: ClientCreate, db: AsyncSession = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    return await client_service.create_client(db, current_user.id, data.model_dump())

@router.get("", response_model=PaginatedResponse[ClientResponse])
async def list_clients(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    active_only: bool = True,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    clients, total = await client_service.get_clients(db, current_user.id, page, size, search, active_only, is_active)
    return PaginatedResponse(items=clients, total=total, page=page, size=size, pages=(total + size - 1) // size if total > 0 else 0)

@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(client_id: str, db: AsyncSession = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    return await client_service.get_client(db, current_user.id, client_id)

@router.patch("/{client_id}", response_model=ClientResponse)
async def update_client(client_id: str, data: ClientUpdate, db: AsyncSession = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    return await client_service.update_client(db, current_user.id, client_id, data.model_dump(exclude_unset=True))

@router.delete("/{client_id}", response_model=ClientResponse)
async def delete_client(client_id: str, db: AsyncSession = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    return await client_service.delete_client(db, current_user.id, client_id)
