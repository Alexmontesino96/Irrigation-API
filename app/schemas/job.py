from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, date

class JobCreate(BaseModel):
    property_id: str
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    job_type: str = "maintenance"
    scheduled_date: date
    price: Optional[float] = Field(None, ge=0)
    reminder_days: Optional[List[int]] = Field(None, description="Days after completion to send reminders, e.g. [30, 90, 180]")
    notes: Optional[str] = None

class JobUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    job_type: Optional[str] = None
    status: Optional[str] = None
    scheduled_date: Optional[date] = None
    completed_date: Optional[date] = None
    price: Optional[float] = Field(None, ge=0)
    reminder_days: Optional[List[int]] = Field(None, description="Days after completion to send reminders")
    notes: Optional[str] = None

class JobResponse(BaseModel):
    id: str
    property_id: str
    title: str
    description: Optional[str] = None
    job_type: str
    status: str
    scheduled_date: date
    completed_date: Optional[date] = None
    price: Optional[float] = None
    reminder_days: Optional[List[int]] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
