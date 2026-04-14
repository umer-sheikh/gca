from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from gulf_climate_agent.contracts.base import ClimateToolOutput


class CarbonFootprintInput(BaseModel):
    country: str
    industry: str
    year: int = Field(ge=1900, le=2100)
    revenue: float = Field(gt=0)


class CarbonFootprintOutput(ClimateToolOutput):
    tCO2e: float
    scopes: dict[str, float] = Field(default_factory=dict)
    methodology: dict[str, Any] = Field(default_factory=dict)
