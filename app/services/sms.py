from datetime import datetime
from typing import Optional
from sqlalchemy import select, func, asc, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.sms_log import SmsLog, SmsStatus, SmsType
from app.models.sms_template import SmsTemplate
from app.models.client import Client
from app.models.reminder import Reminder
from app.models.job import Job
from app.models.property import Property
from app.core.twilio_client import twilio_client
from app.exceptions import NotFoundException, BadRequestException

_SMS_SORT_WHITELIST = {"created_at", "sms_type", "status"}


async def send_sms(db: AsyncSession, owner_id: str, client_id: str, message: str, sms_type: str) -> SmsLog:
    # Get client
    result = await db.execute(
        select(Client).where(Client.id == client_id, Client.owner_id == owner_id)
    )
    client = result.scalar_one_or_none()
    if not client:
        raise NotFoundException("Client not found")
    if not client.phone:
        raise BadRequestException("Client has no phone number")

    # Create log entry
    log = SmsLog(
        owner_id=owner_id,
        client_id=client_id,
        phone_to=client.phone,
        message=message,
        sms_type=sms_type,
        status=SmsStatus.QUEUED.value,
    )
    db.add(log)

    # Send SMS
    try:
        sid = twilio_client.send(client.phone, message)
        log.status = SmsStatus.SENT.value
        log.twilio_sid = sid
        log.sent_at = datetime.utcnow()
    except Exception as e:
        log.status = SmsStatus.FAILED.value
        log.error_message = str(e)

    await db.commit()
    await db.refresh(log)
    return log


async def send_reminder_sms(db: AsyncSession, owner_id: str, reminder_id: str) -> SmsLog:
    # Get reminder with property and client
    result = await db.execute(
        select(Reminder).where(Reminder.id == reminder_id)
    )
    reminder = result.scalar_one_or_none()
    if not reminder:
        raise NotFoundException("Reminder not found")

    # Get property client
    result = await db.execute(
        select(Property).join(Client).where(
            Property.id == reminder.property_id,
            Client.owner_id == owner_id,
        )
    )
    prop = result.scalar_one_or_none()
    if not prop:
        raise NotFoundException("Property not found")

    result = await db.execute(
        select(Client).where(Client.id == prop.client_id, Client.owner_id == owner_id)
    )
    client = result.scalar_one_or_none()
    if not client:
        raise NotFoundException("Client not found")

    message = f"Hola {client.first_name}, le recordamos: {reminder.title}. Fecha: {reminder.remind_date}"

    return await send_sms(db, owner_id, client.id, message, SmsType.REMINDER.value)


async def get_sms_logs(
    db: AsyncSession,
    owner_id: str,
    page: int = 1,
    size: int = 20,
    client_id: Optional[str] = None,
    sms_type: Optional[str] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
) -> tuple[list[SmsLog], int]:
    query = select(SmsLog).where(SmsLog.owner_id == owner_id)
    count_query = select(func.count()).select_from(SmsLog).where(SmsLog.owner_id == owner_id)

    if client_id:
        query = query.where(SmsLog.client_id == client_id)
        count_query = count_query.where(SmsLog.client_id == client_id)
    if sms_type:
        query = query.where(SmsLog.sms_type == sms_type)
        count_query = count_query.where(SmsLog.sms_type == sms_type)

    total_result = await db.execute(count_query)
    total = total_result.scalar()

    col = getattr(SmsLog, sort_by) if sort_by in _SMS_SORT_WHITELIST else SmsLog.created_at
    order_fn = asc if sort_order == "asc" else desc
    query = query.order_by(order_fn(col)).offset((page - 1) * size).limit(size)

    result = await db.execute(query)
    logs = list(result.scalars().all())
    return logs, total


# Template CRUD
async def create_template(db: AsyncSession, owner_id: str, data: dict) -> SmsTemplate:
    template = SmsTemplate(owner_id=owner_id, **data)
    db.add(template)
    await db.commit()
    await db.refresh(template)
    return template


async def get_templates(db: AsyncSession, owner_id: str) -> list[SmsTemplate]:
    result = await db.execute(
        select(SmsTemplate).where(SmsTemplate.owner_id == owner_id).order_by(SmsTemplate.name)
    )
    return list(result.scalars().all())


async def get_template(db: AsyncSession, template_id: str, owner_id: str) -> SmsTemplate:
    result = await db.execute(
        select(SmsTemplate).where(SmsTemplate.id == template_id, SmsTemplate.owner_id == owner_id)
    )
    template = result.scalar_one_or_none()
    if not template:
        raise NotFoundException("Template not found")
    return template


async def update_template(db: AsyncSession, template_id: str, owner_id: str, data: dict) -> SmsTemplate:
    template = await get_template(db, template_id, owner_id)
    for key, value in data.items():
        if value is not None:
            setattr(template, key, value)
    await db.commit()
    await db.refresh(template)
    return template


async def delete_template(db: AsyncSession, template_id: str, owner_id: str) -> None:
    template = await get_template(db, template_id, owner_id)
    await db.delete(template)
    await db.commit()
