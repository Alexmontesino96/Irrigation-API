from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date


class ExpenseCreate(BaseModel):
    category: str
    description: str = Field(..., min_length=1, max_length=200)
    amount: float = Field(..., gt=0)
    expense_date: date
    job_id: Optional[str] = None


class ExpenseUpdate(BaseModel):
    category: Optional[str] = None
    description: Optional[str] = Field(None, min_length=1, max_length=200)
    amount: Optional[float] = Field(None, gt=0)
    expense_date: Optional[date] = None
    job_id: Optional[str] = None


class ExpenseResponse(BaseModel):
    id: str
    owner_id: str
    job_id: Optional[str] = None
    category: str
    description: str
    amount: float
    expense_date: date
    receipt_url: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ExpenseSummary(BaseModel):
    category: str
    total: float
    count: int
