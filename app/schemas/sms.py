from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class SmsSendRequest(BaseModel):
    client_id: str
    message: str = Field(..., min_length=1, max_length=1600)
    sms_type: str = "custom"


class SmsLogResponse(BaseModel):
    id: str
    owner_id: str
    client_id: str
    phone_to: str
    message: str
    sms_type: str
    status: str
    twilio_sid: Optional[str] = None
    error_message: Optional[str] = None
    sent_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class SmsTemplateCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    sms_type: str
    body: str = Field(..., min_length=1)


class SmsTemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    sms_type: Optional[str] = None
    body: Optional[str] = Field(None, min_length=1)
    is_active: Optional[bool] = None


class SmsTemplateResponse(BaseModel):
    id: str
    owner_id: str
    name: str
    sms_type: str
    body: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
