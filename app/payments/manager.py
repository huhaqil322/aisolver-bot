from __future__ import annotations

from dataclasses import dataclass

from app.config.settings import get_settings

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


PLAN: PlanFeatures = PlanFeatures(
    daily_limit=settings.DAILY_LIMIT,
    monthly_tokens=settings.TOKENS_PER_MONTH,
    all_models=True,
    no_ads=True,
)
