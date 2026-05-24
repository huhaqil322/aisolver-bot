from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional

from app.config.settings import SubscriptionTier, get_settings

settings = get_settings()


@dataclass
class PlanFeatures:
    daily_limit: int
    monthly_tokens: int
    priority_support: bool = False
    all_models: bool = False
    api_access: bool = False
    team_access: bool = False
    custom_models: bool = False
    no_ads: bool = True


PLANS: dict[SubscriptionTier, PlanFeatures] = {
    SubscriptionTier.FREE: PlanFeatures(
        daily_limit=settings.FREE_DAILY_LIMIT,
        monthly_tokens=settings.FREE_TOKENS_PER_MONTH,
        all_models=False,
        no_ads=False,
    ),
    SubscriptionTier.BASIC: PlanFeatures(
        daily_limit=settings.BASIC_DAILY_LIMIT,
        monthly_tokens=settings.BASIC_TOKENS_PER_MONTH,
        all_models=True,
        priority_support=False,
    ),
    SubscriptionTier.PREMIUM: PlanFeatures(
        daily_limit=settings.PREMIUM_DAILY_LIMIT,
        monthly_tokens=settings.PREMIUM_TOKENS_PER_MONTH,
        priority_support=True,
        all_models=True,
        api_access=True,
    ),
    SubscriptionTier.ENTERPRISE: PlanFeatures(
        daily_limit=999999,
        monthly_tokens=99999999,
        priority_support=True,
        all_models=True,
        api_access=True,
        team_access=True,
        custom_models=True,
    ),
}


class SubscriptionManager:
    @staticmethod
    def get_plan_features(tier: SubscriptionTier) -> PlanFeatures:
        return PLANS.get(tier, PLANS[SubscriptionTier.FREE])

    @staticmethod
    def check_daily_limit(
        tier: SubscriptionTier, current_requests: int
    ) -> bool:
        features = PLANS.get(tier, PLANS[SubscriptionTier.FREE])
        return current_requests < features.daily_limit

    @staticmethod
    def check_monthly_tokens(
        tier: SubscriptionTier, current_tokens: int
    ) -> bool:
        features = PLANS.get(tier, PLANS[SubscriptionTier.FREE])
        return current_tokens < features.monthly_tokens

    @staticmethod
    def calculate_trial_end() -> datetime:
        return datetime.now(timezone.utc) + timedelta(days=settings.TRIAL_DAYS)

    @staticmethod
    def get_referral_bonus_end(date: Optional[datetime] = None) -> datetime:
        start = date or datetime.now(timezone.utc)
        return start + timedelta(days=settings.REFERRAL_BONUS_DAYS)
