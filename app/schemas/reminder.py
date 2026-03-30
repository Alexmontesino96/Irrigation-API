from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date

class ReminderCreate(BaseModel):
    job_id: Optional[str] = None
    property_id: str
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    remind_date: date

class ReminderUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    remind_date: Optional[date] = None
    status: Optional[str] = None

class ReminderResponse(BaseModel):
    id: str
    job_id: Optional[str] = None
    property_id: str
    title: str
    description: Optional[str] = None
    remind_date: date
    status: str
    is_auto_generated: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
