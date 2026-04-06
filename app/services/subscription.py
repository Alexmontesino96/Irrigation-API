import os
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.subscription import Subscription, PlanTier, SubscriptionStatus
from app.core.stripe_client import stripe_client
from app.exceptions import NotFoundException


PLAN_PRICES = {
    "starter": os.getenv("STRIPE_PRICE_STARTER", ""),
    "professional": os.getenv("STRIPE_PRICE_PROFESSIONAL", ""),
    "premium": os.getenv("STRIPE_PRICE_PREMIUM", ""),
}

PLAN_FEATURES = {
    "starter": {"clients", "properties", "jobs", "reminders"},
    "professional": {"clients", "properties", "jobs", "reminders", "invoices", "calendar", "analytics"},
    "premium": {"clients", "properties", "jobs", "reminders", "invoices", "calendar", "analytics", "sms", "expenses", "unlimited"},
}


async def get_subscription(db: AsyncSession, owner_id: str) -> Subscription | None:
    result = await db.execute(
        select(Subscription).where(Subscription.owner_id == owner_id)
    )
    return result.scalar_one_or_none()


async def get_or_create_subscription(db: AsyncSession, owner_id: str) -> Subscription:
    sub = await get_subscription(db, owner_id)
    if not sub:
        sub = Subscription(
            owner_id=owner_id,
            plan=PlanTier.STARTER.value,
            status=SubscriptionStatus.ACTIVE.value,
        )
        db.add(sub)
        await db.commit()
        await db.refresh(sub)
    return sub


async def create_checkout(db: AsyncSession, owner_id: str, email: str, name: str, plan: str, success_url: str, cancel_url: str) -> str | None:
    sub = await get_or_create_subscription(db, owner_id)

    if not sub.stripe_customer_id:
        customer_id = stripe_client.create_customer(email, name)
        if customer_id:
            sub.stripe_customer_id = customer_id
            await db.commit()

    if not sub.stripe_customer_id:
        return None

    price_id = PLAN_PRICES.get(plan)
    if not price_id:
        return None

    return stripe_client.create_checkout_session(sub.stripe_customer_id, price_id, success_url, cancel_url)


async def create_portal(db: AsyncSession, owner_id: str) -> str | None:
    sub = await get_subscription(db, owner_id)
    if not sub or not sub.stripe_customer_id:
        return None
    return stripe_client.create_portal_session(sub.stripe_customer_id)


async def handle_stripe_event(db: AsyncSession, event: dict) -> None:
    event_type = event.get("type", "")
    data = event.get("data", {}).get("object", {})

    if event_type == "checkout.session.completed":
        customer_id = data.get("customer")
        result = await db.execute(
            select(Subscription).where(Subscription.stripe_customer_id == customer_id)
        )
        sub = result.scalar_one_or_none()
        if sub:
            sub.status = SubscriptionStatus.ACTIVE.value
            sub.stripe_subscription_id = data.get("subscription")
            await db.commit()

    elif event_type in ("customer.subscription.updated", "customer.subscription.deleted"):
        sub_id = data.get("id")
        result = await db.execute(
            select(Subscription).where(Subscription.stripe_subscription_id == sub_id)
        )
        sub = result.scalar_one_or_none()
        if sub:
            status = data.get("status", "")
            if status == "active":
                sub.status = SubscriptionStatus.ACTIVE.value
            elif status == "past_due":
                sub.status = SubscriptionStatus.PAST_DUE.value
            elif status in ("canceled", "unpaid"):
                sub.status = SubscriptionStatus.CANCELLED.value
            await db.commit()


def check_feature_access(plan: str, feature: str) -> bool:
    plan_features = PLAN_FEATURES.get(plan, set())
    return feature in plan_features
