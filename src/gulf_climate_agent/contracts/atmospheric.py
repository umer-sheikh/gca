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


class LatLonHorizonInput(BaseModel):
    lat: Latitude
    lon: Longitude
    horizon: int = Field(ge=1, le=30)


class LatLonInput(BaseModel):
    lat: Latitude
    lon: Longitude


class AQIInquiryOutput(ClimateToolOutput):
    aqi: dict[str, Any]
    pollutants: dict[str, Any]


class AQIPredictionOutput(ClimateToolOutput):
    aqi_time_series: TimeSeries


class AQIAnalysisOutput(ClimateToolOutput):
    stats: dict[str, Any]
    trend: dict[str, Any]
    exceedances: dict[str, int]


class PollenForecastOutput(ClimateToolOutput):
    pollen_levels: TimeSeries


class UVIndexForecastOutput(ClimateToolOutput):
    uv_time_series: TimeSeries
