from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.property import Property
from app.models.client import Client
from app.exceptions import NotFoundException, ForbiddenException

async def _verify_client_ownership(db: AsyncSession, client_id: str, owner_id: str) -> Client:
    result = await db.execute(select(Client).where(Client.id == client_id, Client.owner_id == owner_id))
    client = result.scalar_one_or_none()
    if not client:
        raise NotFoundException("Client not found")
    return client

async def create_property(db: AsyncSession, owner_id: str, client_id: str, data: dict) -> Property:
    await _verify_client_ownership(db, client_id, owner_id)
    prop = Property(client_id=client_id, **data)
    db.add(prop)
    await db.commit()
    await db.refresh(prop)
    return prop

async def get_properties(db: AsyncSession, owner_id: str, client_id: str, page: int = 1, size: int = 20) -> tuple[list[Property], int]:
    await _verify_client_ownership(db, client_id, owner_id)

    count_query = select(func.count()).select_from(Property).where(Property.client_id == client_id)
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    query = select(Property).where(Property.client_id == client_id).order_by(Property.created_at.desc()).offset((page - 1) * size).limit(size)
    result = await db.execute(query)
    properties = list(result.scalars().all())
    return properties, total

async def get_property(db: AsyncSession, owner_id: str, property_id: str) -> Property:
    result = await db.execute(
        select(Property).join(Client).where(Property.id == property_id, Client.owner_id == owner_id)
    )
    prop = result.scalar_one_or_none()
    if not prop:
        raise NotFoundException("Property not found")
    return prop

async def update_property(db: AsyncSession, owner_id: str, property_id: str, data: dict) -> Property:
    prop = await get_property(db, owner_id, property_id)
    for key, value in data.items():
        if value is not None:
            setattr(prop, key, value)
    await db.commit()
    await db.refresh(prop)
    return prop

async def delete_property(db: AsyncSession, owner_id: str, property_id: str) -> None:
    prop = await get_property(db, owner_id, property_id)
    await db.delete(prop)
    await db.commit()


_PROPERTY_SORT_WHITELIST = {"name", "address", "city", "created_at", "updated_at"}


async def get_all_properties(
    db: AsyncSession,
    owner_id: str,
    page: int = 1,
    size: int = 20,
    search: str | None = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
) -> tuple[list[Property], int]:
    """Return all properties across all clients owned by owner_id."""
    from sqlalchemy import asc, desc as _desc
    from sqlalchemy.orm import selectinload

    base = select(Property).join(Client).where(Client.owner_id == owner_id).options(selectinload(Property.client))
    count_base = select(func.count()).select_from(Property).join(Client).where(Client.owner_id == owner_id)

    if search:
        search_filter = f"%{search}%"
        search_cond = (
            Property.name.ilike(search_filter)
            | Property.address.ilike(search_filter)
        )
        base = base.where(search_cond)
        count_base = count_base.where(search_cond)

    total_result = await db.execute(count_base)
    total = total_result.scalar()

    col = (
        getattr(Property, sort_by)
        if sort_by in _PROPERTY_SORT_WHITELIST
        else Property.created_at
    )
    order_fn = asc if sort_order == "asc" else _desc
    query = base.order_by(order_fn(col)).offset((page - 1) * size).limit(size)

    result = await db.execute(query)
    properties = list(result.scalars().all())
    return properties, total
