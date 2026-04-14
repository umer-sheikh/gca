from __future__ import annotations

from typing import Any, Annotated

from pydantic import BaseModel, Field, field_validator

from gulf_climate_agent.contracts.base import ArtifactRef, ClimateToolOutput, NumericStats


Latitude = Annotated[float, Field(ge=-90.0, le=90.0)]
Longitude = Annotated[float, Field(ge=-180.0, le=180.0)]


class GetSatelliteImageInput(BaseModel):
    lat: Latitude
    lon: Longitude
    date: str

    @field_validator("date")
    @classmethod
    def validate_date(cls, value: str) -> str:
        if len(value) != 10 or value.count("-") != 2:
            raise ValueError("date must be in YYYY-MM-DD format")
        return value


class SatelliteImageOutput(ClimateToolOutput):
    rgb_img: ArtifactRef
    ndvi_index: ArtifactRef
    ndwi_index: ArtifactRef
    image_ref: ArtifactRef
    metadata: dict[str, Any] = Field(default_factory=dict)


class CalculateNdviInput(BaseModel):
    image: str


class CalculateNdwiInput(BaseModel):
    image: str


class IndexStats(NumericStats):
    valid_fraction: float | None = None
    positive_fraction: float | None = None
    negative_fraction: float | None = None
    threshold_fraction: float | None = None


class NdviOutput(ClimateToolOutput):
    ndvi_map: ArtifactRef
    stats: IndexStats


class NdwiOutput(ClimateToolOutput):
    ndwi_map: ArtifactRef
    stats: IndexStats


class DesertificationAnalysisInput(BaseModel):
    image1: str
    image2: str


class DesertificationMetrics(BaseModel):
    valid_pixels: int
    mean_ndvi_delta: float
    mean_ndwi_delta: float
    degraded_fraction: float
    severe_fraction: float
    moisture_loss_fraction: float
    vegetation_gain_fraction: float


class DesertificationOutput(ClimateToolOutput):
    change_map: ArtifactRef
    metrics: DesertificationMetrics
    analysis: str
