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
