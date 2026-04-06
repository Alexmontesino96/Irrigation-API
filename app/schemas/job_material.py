from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class JobMaterialCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    quantity: int = Field(1, ge=1)
    unit_cost: float = Field(..., ge=0)


class JobMaterialUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    quantity: Optional[int] = Field(None, ge=1)
    unit_cost: Optional[float] = Field(None, ge=0)


class JobMaterialResponse(BaseModel):
    id: str
    job_id: str
    name: str
    quantity: int
    unit_cost: float
    total: float = 0
    created_at: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_material(cls, mat) -> "JobMaterialResponse":
        data = cls.model_validate(mat)
        data.total = round(mat.quantity * float(mat.unit_cost), 2)
        return data
