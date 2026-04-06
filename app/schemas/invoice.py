from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date


class InvoiceItemCreate(BaseModel):
    description: str = Field(..., min_length=1, max_length=200)
    quantity: int = Field(1, ge=1)
    unit_price: float = Field(..., ge=0)
    job_id: Optional[str] = None


class InvoiceItemResponse(BaseModel):
    id: str
    invoice_id: str
    description: str
    quantity: int
    unit_price: float
    total: float
    job_id: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class InvoiceCreate(BaseModel):
    client_id: str
    issue_date: date
    due_date: date
    tax_rate: float = Field(0, ge=0)
    notes: Optional[str] = None
    items: List[InvoiceItemCreate]


class InvoiceUpdate(BaseModel):
    status: Optional[str] = None
    due_date: Optional[date] = None
    tax_rate: Optional[float] = Field(None, ge=0)
    notes: Optional[str] = None
    paid_date: Optional[date] = None


class InvoiceResponse(BaseModel):
    id: str
    owner_id: str
    client_id: str
    invoice_number: str
    status: str
    issue_date: date
    due_date: date
    subtotal: float
    tax_rate: float
    tax_amount: float
    total: float
    notes: Optional[str] = None
    paid_date: Optional[date] = None
    client_name: Optional[str] = None
    items: List[InvoiceItemResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_invoice(cls, inv) -> "InvoiceResponse":
        data = cls.model_validate(inv)
        if hasattr(inv, "client") and inv.client:
            data.client_name = f"{inv.client.first_name} {inv.client.last_name}"
        return data


class InvoiceSummary(BaseModel):
    status: str
    total: float
    count: int
