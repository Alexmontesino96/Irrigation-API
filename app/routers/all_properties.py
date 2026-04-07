from fastapi import APIRouter, Depends, Query
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.dependencies import get_current_user, CurrentUser
from app.schemas.property import PropertyWithClientResponse
from app.schemas.common import PaginatedResponse
from app.services import property as property_service

router = APIRouter(prefix="/api/properties", tags=["properties (global)"])


@router.get("", response_model=PaginatedResponse[PropertyWithClientResponse])
async def list_all_properties(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    properties, total = await property_service.get_all_properties(
        db,
        current_user.id,
        page=page,
        size=size,
        search=search,
        sort_by=sort_by or "created_at",
        sort_order=sort_order or "desc",
    )

    items = []
    for prop in properties:
        client = prop.client
        items.append(
            PropertyWithClientResponse(
                id=prop.id,
                client_id=prop.client_id,
                client_name=f"{client.first_name} {client.last_name}",
                name=prop.name,
                address=prop.address,
                city=prop.city,
                state=prop.state,
                zip_code=prop.zip_code,
                notes=prop.notes,
                created_at=prop.created_at,
                updated_at=prop.updated_at,
            )
        )

    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size if total > 0 else 0,
    )
