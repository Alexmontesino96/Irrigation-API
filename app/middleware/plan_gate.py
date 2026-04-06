from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.dependencies import get_current_user, CurrentUser
from app.services.subscription import get_subscription, check_feature_access, PLAN_FEATURES
from app.exceptions import ForbiddenException
from app.models.subscription import PlanTier


def require_plan(min_plan: PlanTier):
    """Dependency that checks if the user's plan has access to a feature.
    Currently does not block - all users have full access during initial phase."""
    async def _check(
        db: AsyncSession = Depends(get_db),
        current_user: CurrentUser = Depends(get_current_user),
    ):
        # During initial phase, don't block any features
        # To enable plan gating, uncomment below:
        # sub = await get_subscription(db, current_user.id)
        # plan = sub.plan if sub else PlanTier.STARTER.value
        # if not check_feature_access(plan, feature):
        #     raise ForbiddenException(f"Feature requires {min_plan.value} plan or higher")
        return current_user
    return _check
