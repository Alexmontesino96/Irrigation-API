from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class PropertyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    address: str = Field(..., max_length=500)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=50)
    zip_code: Optional[str] = Field(None, max_length=10)
    notes: Optional[str] = None

class PropertyUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    address: Optional[str] = Field(None, max_length=500)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=50)
    zip_code: Optional[str] = Field(None, max_length=10)
    notes: Optional[str] = None

class PropertyResponse(BaseModel):
    id: str
    client_id: str
    name: str
    address: str
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PropertyWithClientResponse(PropertyResponse):
    client_id: str
    client_name: str

    model_config = {"from_attributes": True}
