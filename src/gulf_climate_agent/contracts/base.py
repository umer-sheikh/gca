from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


def utc_now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


class ArtifactRef(BaseModel):
    uri: str
    media_type: str
    kind: str
    size_bytes: int | None = None
    sha256: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class OutputMeta(BaseModel):
    provider: str
    source: str | None = None
    generated_at: str = Field(default_factory=utc_now_iso)
    units: dict[str, str] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)
    location: dict[str, Any] | None = None
    timestamps: dict[str, str] = Field(default_factory=dict)


class ClimateToolOutput(BaseModel):
    meta: OutputMeta


class NumericStats(BaseModel):
    count: int
    min: float | None = None
    max: float | None = None
    mean: float | None = None
    median: float | None = None
    std: float | None = None


class TimeSeries(BaseModel):
    timestamps: list[str]
    values: dict[str, list[float | None]]
    units: dict[str, str] = Field(default_factory=dict)
