from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date

class IrrigationSystemCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    system_type: str = Field(..., max_length=50)
    zone_count: Optional[int] = Field(None, ge=1)
    install_date: Optional[date] = None
    notes: Optional[str] = None

class IrrigationSystemUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    system_type: Optional[str] = Field(None, max_length=50)
    zone_count: Optional[int] = Field(None, ge=1)
    install_date: Optional[date] = None
    notes: Optional[str] = None

class IrrigationSystemResponse(BaseModel):
    id: str
    property_id: str
    name: str
    system_type: str
    zone_count: Optional[int] = None
    install_date: Optional[date] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
