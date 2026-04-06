from fastapi import APIRouter, Depends, Query
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.dependencies import get_current_user, CurrentUser
from app.schemas.sms import SmsSendRequest, SmsLogResponse, SmsTemplateCreate, SmsTemplateUpdate, SmsTemplateResponse
from app.schemas.common import PaginatedResponse
from app.services import sms as sms_service

router = APIRouter(prefix="/api/sms", tags=["sms"])


@router.post("/send", response_model=SmsLogResponse, status_code=201)
async def send_sms(
    data: SmsSendRequest,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    return await sms_service.send_sms(db, current_user.id, data.client_id, data.message, data.sms_type)


@router.post("/send-reminder/{reminder_id}", response_model=SmsLogResponse, status_code=201)
async def send_reminder_sms(
    reminder_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    return await sms_service.send_reminder_sms(db, current_user.id, reminder_id)


@router.get("/logs", response_model=PaginatedResponse[SmsLogResponse])
async def list_sms_logs(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    client_id: Optional[str] = None,
    sms_type: Optional[str] = None,
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    logs, total = await sms_service.get_sms_logs(
        db, current_user.id, page, size, client_id, sms_type,
        sort_by=sort_by or "created_at", sort_order=sort_order or "desc"
    )
    return PaginatedResponse(
        items=logs, total=total, page=page, size=size,
        pages=(total + size - 1) // size if total > 0 else 0
    )


# Templates
@router.post("/templates", response_model=SmsTemplateResponse, status_code=201)
async def create_template(
    data: SmsTemplateCreate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    return await sms_service.create_template(db, current_user.id, data.model_dump())


@router.get("/templates", response_model=list[SmsTemplateResponse])
async def list_templates(
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    return await sms_service.get_templates(db, current_user.id)


@router.get("/templates/{template_id}", response_model=SmsTemplateResponse)
async def get_template(
    template_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    return await sms_service.get_template(db, template_id, current_user.id)


@router.patch("/templates/{template_id}", response_model=SmsTemplateResponse)
async def update_template(
    template_id: str,
    data: SmsTemplateUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    return await sms_service.update_template(db, template_id, current_user.id, data.model_dump(exclude_unset=True))


@router.delete("/templates/{template_id}", status_code=204)
async def delete_template(
    template_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    await sms_service.delete_template(db, template_id, current_user.id)
