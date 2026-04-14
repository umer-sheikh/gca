from __future__ import annotations

from typing import Annotated, Any

from pydantic import BaseModel, Field, field_validator

from gulf_climate_agent.contracts.base import ClimateToolOutput, TimeSeries


Latitude = Annotated[float, Field(ge=-90.0, le=90.0)]
Longitude = Annotated[float, Field(ge=-180.0, le=180.0)]


class LatLonDateInput(BaseModel):
    lat: Latitude
    lon: Longitude
    date: str

    @field_validator("date")
    @classmethod
    def validate_date(cls, value: str) -> str:
        if len(value) != 10 or value.count("-") != 2:
            raise ValueError("date must be in YYYY-MM-DD format")
        return value


class LatLonRangeInput(BaseModel):
    lat: Latitude
    lon: Longitude
    start: str
    end: str


class LatLonDaysInput(BaseModel):
    lat: Latitude
    lon: Longitude
    days: int = Field(ge=1, le=30)


class LatLonHorizonInput(BaseModel):
    lat: Latitude
    lon: Longitude
    horizon: int = Field(ge=1, le=30)


class GeocodeMappingInput(BaseModel):
    region: str


class GeocodeMappingOutput(ClimateToolOutput):
    lat: float
    lon: float
    metadata: dict[str, Any] = Field(default_factory=dict)


class WeatherInquiryOutput(ClimateToolOutput):
    weather: dict[str, Any]


class WeatherForecastOutput(ClimateToolOutput):
    forecast_series: dict[str, Any]


class WeatherAnalysisOutput(ClimateToolOutput):
    stats: dict[str, Any]
    anomalies: dict[str, Any]


class RainInquiryOutput(ClimateToolOutput):
    precip_mm: float | None


class RainPredictionOutput(ClimateToolOutput):
    precip_series: TimeSeries


class RainAnalysisOutput(ClimateToolOutput):
    stats: dict[str, Any]
    events: list[dict[str, Any]]


class RiverDischargeOutput(ClimateToolOutput):
    discharge_m3_s: float | None
