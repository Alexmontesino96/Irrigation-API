from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.irrigation_system import IrrigationSystem
from app.models.property import Property
from app.models.client import Client
from app.exceptions import NotFoundException
from app.services.property import get_property as verify_property_ownership

async def create_irrigation_system(db: AsyncSession, owner_id: str, property_id: str, data: dict) -> IrrigationSystem:
    await verify_property_ownership(db, owner_id, property_id)
    system = IrrigationSystem(property_id=property_id, **data)
    db.add(system)
    await db.commit()
    await db.refresh(system)
    return system

async def get_irrigation_systems(db: AsyncSession, owner_id: str, property_id: str, page: int = 1, size: int = 20) -> tuple[list[IrrigationSystem], int]:
    await verify_property_ownership(db, owner_id, property_id)

    count_query = select(func.count()).select_from(IrrigationSystem).where(IrrigationSystem.property_id == property_id)
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    query = select(IrrigationSystem).where(IrrigationSystem.property_id == property_id).order_by(IrrigationSystem.created_at.desc()).offset((page - 1) * size).limit(size)
    result = await db.execute(query)
    systems = list(result.scalars().all())
    return systems, total

async def get_irrigation_system(db: AsyncSession, owner_id: str, system_id: str) -> IrrigationSystem:
    result = await db.execute(
        select(IrrigationSystem).join(Property).join(Client).where(
            IrrigationSystem.id == system_id, Client.owner_id == owner_id
        )
    )
    system = result.scalar_one_or_none()
    if not system:
        raise NotFoundException("Irrigation system not found")
    return system

async def update_irrigation_system(db: AsyncSession, owner_id: str, system_id: str, data: dict) -> IrrigationSystem:
    system = await get_irrigation_system(db, owner_id, system_id)
    for key, value in data.items():
        if value is not None:
            setattr(system, key, value)
    await db.commit()
    await db.refresh(system)
    return system

async def delete_irrigation_system(db: AsyncSession, owner_id: str, system_id: str) -> None:
    system = await get_irrigation_system(db, owner_id, system_id)
    await db.delete(system)
    await db.commit()
