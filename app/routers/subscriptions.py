from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.dependencies import get_current_user, CurrentUser
from app.schemas.subscription import SubscriptionResponse, CheckoutRequest, CheckoutResponse, PortalResponse
from app.services import subscription as sub_service
from app.core.stripe_client import stripe_client

router = APIRouter(prefix="/api/subscriptions", tags=["subscriptions"])


@router.get("/current", response_model=SubscriptionResponse)
async def get_current_subscription(
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    sub = await sub_service.get_or_create_subscription(db, current_user.id)
    return sub


@router.post("/checkout", response_model=CheckoutResponse)
async def create_checkout(
    data: CheckoutRequest,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    url = await sub_service.create_checkout(
        db, current_user.id, current_user.email, "",
        data.plan, data.success_url, data.cancel_url
    )
    return CheckoutResponse(checkout_url=url)


@router.post("/portal", response_model=PortalResponse)
async def create_portal(
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    url = await sub_service.create_portal(db, current_user.id)
    return PortalResponse(portal_url=url)


@router.post("/webhook")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    payload = await request.body()
    sig = request.headers.get("stripe-signature", "")
    event = stripe_client.verify_webhook(payload, sig)
    if event:
        await sub_service.handle_stripe_event(db, event)
    return {"status": "ok"}
