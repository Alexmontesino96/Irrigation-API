from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SubscriptionResponse(BaseModel):
    id: str
    owner_id: str
    plan: str
    status: str
    stripe_customer_id: Optional[str] = None
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class CheckoutRequest(BaseModel):
    plan: str
    success_url: str
    cancel_url: str


class CheckoutResponse(BaseModel):
    checkout_url: Optional[str] = None


class PortalResponse(BaseModel):
    portal_url: Optional[str] = None
