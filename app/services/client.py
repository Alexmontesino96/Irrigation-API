from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.client import Client
from app.exceptions import NotFoundException

async def create_client(db: AsyncSession, owner_id: str, data: dict) -> Client:
    client = Client(owner_id=owner_id, **data)
    db.add(client)
    await db.commit()
    await db.refresh(client)
    return client

async def get_clients(db: AsyncSession, owner_id: str, page: int = 1, size: int = 20, search: Optional[str] = None, active_only: bool = True, is_active: Optional[bool] = None) -> tuple[list[Client], int]:
    query = select(Client).where(Client.owner_id == owner_id)
    count_query = select(func.count()).select_from(Client).where(Client.owner_id == owner_id)

    # is_active takes priority over active_only for explicit filtering
    if is_active is not None:
        query = query.where(Client.is_active == is_active)
        count_query = count_query.where(Client.is_active == is_active)
    elif active_only:
        query = query.where(Client.is_active == True)
        count_query = count_query.where(Client.is_active == True)

    if search:
        search_filter = f"%{search}%"
        query = query.where(
            (Client.first_name.ilike(search_filter)) |
            (Client.last_name.ilike(search_filter)) |
            (Client.email.ilike(search_filter)) |
            (Client.phone.ilike(search_filter))
        )
        count_query = count_query.where(
            (Client.first_name.ilike(search_filter)) |
            (Client.last_name.ilike(search_filter)) |
            (Client.email.ilike(search_filter)) |
            (Client.phone.ilike(search_filter))
        )

    total_result = await db.execute(count_query)
    total = total_result.scalar()

    query = query.order_by(Client.created_at.desc()).offset((page - 1) * size).limit(size)
    result = await db.execute(query)
    clients = list(result.scalars().all())

    return clients, total

async def get_client(db: AsyncSession, owner_id: str, client_id: str) -> Client:
    result = await db.execute(
        select(Client).where(Client.id == client_id, Client.owner_id == owner_id)
    )
    client = result.scalar_one_or_none()
    if not client:
        raise NotFoundException("Client not found")
    return client

async def update_client(db: AsyncSession, owner_id: str, client_id: str, data: dict) -> Client:
    client = await get_client(db, owner_id, client_id)
    for key, value in data.items():
        if value is not None:
            setattr(client, key, value)
    await db.commit()
    await db.refresh(client)
    return client

async def delete_client(db: AsyncSession, owner_id: str, client_id: str) -> Client:
    """Soft delete - sets is_active to False"""
    client = await get_client(db, owner_id, client_id)
    client.is_active = False
    await db.commit()
    await db.refresh(client)
    return client
