from __future__ import annotations

from gulf_climate_agent.contracts.atmospheric import (
    AQIAnalysisOutput,
    AQIInquiryOutput,
    AQIPredictionOutput,
    LatLonDateInput,
    LatLonHorizonInput,
    LatLonInput,
    LatLonRangeInput,
    PollenForecastOutput,
    UVIndexForecastOutput,
)
from gulf_climate_agent.contracts.base import TimeSeries
from gulf_climate_agent.tools.base import ToolServices, build_meta, dump_model, make_structured_tool


ATMOSPHERIC_DESCRIPTIONS = {
    "aqi_inquiry": "Return AQI and pollutant values for a location and date.",
    "aqi_prediction": "Forecast AQI for a location over a specified horizon.",
    "aqi_analysis": "Summarize AQI trends and exceedances over a date range.",
    "pollen_forecast": "Return forecast pollen levels for a location.",
    "uv_index_forecast": "Return UV index forecast for a location.",
}


def build_atmospheric_tools(services: ToolServices):
    open_meteo = services.open_meteo

    def aqi_inquiry(lat: float, lon: float, date: str):
        payload = LatLonDateInput(lat=lat, lon=lon, date=date)
        result = open_meteo.aqi_inquiry(lat=payload.lat, lon=payload.lon, date=payload.date)
        output = AQIInquiryOutput(
            meta=build_meta(
                provider="open-meteo",
                source=services.settings.open_meteo.air_quality_url,
                units=result.get("units", {}),
                location={"lat": payload.lat, "lon": payload.lon},
                timestamps={"date": payload.date},
            ),
            aqi=result["aqi"],
            pollutants=result["pollutants"],
        )
        return dump_model(output)

    def aqi_prediction(lat: float, lon: float, horizon: int):
        payload = LatLonHorizonInput(lat=lat, lon=lon, horizon=horizon)
        result = open_meteo.aqi_prediction(lat=payload.lat, lon=payload.lon, horizon=payload.horizon)
        output = AQIPredictionOutput(
            meta=build_meta(
                provider="open-meteo",
                source=services.settings.open_meteo.air_quality_url,
                units=result["aqi_time_series"].get("units", {}),
                location={"lat": payload.lat, "lon": payload.lon},
            ),
            aqi_time_series=TimeSeries(**result["aqi_time_series"]),
        )
        return dump_model(output)

    def aqi_analysis(lat: float, lon: float, start: str, end: str):
        payload = LatLonRangeInput(lat=lat, lon=lon, start=start, end=end)
        result = open_meteo.aqi_analysis(lat=payload.lat, lon=payload.lon, start=payload.start, end=payload.end)
        output = AQIAnalysisOutput(
            meta=build_meta(
                provider="open-meteo",
                source=services.settings.open_meteo.air_quality_url,
                units=result.get("units", {}),
                location={"lat": payload.lat, "lon": payload.lon},
                timestamps={"start": payload.start, "end": payload.end},
            ),
            stats=result["stats"],
            trend=result["trend"],
            exceedances=result["exceedances"],
        )
        return dump_model(output)

    def pollen_forecast(lat: float, lon: float):
        payload = LatLonInput(lat=lat, lon=lon)
        result = open_meteo.pollen_forecast(lat=payload.lat, lon=payload.lon)
        output = PollenForecastOutput(
            meta=build_meta(
                provider="open-meteo",
                source=services.settings.open_meteo.air_quality_url,
                units=result["pollen_levels"].get("units", {}),
                location={"lat": payload.lat, "lon": payload.lon},
            ),
            pollen_levels=TimeSeries(**result["pollen_levels"]),
        )
        return dump_model(output)

    def uv_index_forecast(lat: float, lon: float):
        payload = LatLonInput(lat=lat, lon=lon)
        result = open_meteo.uv_index_forecast(lat=payload.lat, lon=payload.lon)
        output = UVIndexForecastOutput(
            meta=build_meta(
                provider="open-meteo",
                source=services.settings.open_meteo.weather_url,
                units=result["uv_time_series"].get("units", {}),
                location={"lat": payload.lat, "lon": payload.lon},
            ),
            uv_time_series=TimeSeries(**result["uv_time_series"]),
        )
        return dump_model(output)

    return [
        make_structured_tool(
            name="aqi_inquiry",
            description=ATMOSPHERIC_DESCRIPTIONS["aqi_inquiry"],
            args_schema=LatLonDateInput,
            fn=aqi_inquiry,
        ),
        make_structured_tool(
            name="aqi_prediction",
            description=ATMOSPHERIC_DESCRIPTIONS["aqi_prediction"],
            args_schema=LatLonHorizonInput,
            fn=aqi_prediction,
        ),
        make_structured_tool(
            name="aqi_analysis",
            description=ATMOSPHERIC_DESCRIPTIONS["aqi_analysis"],
            args_schema=LatLonRangeInput,
            fn=aqi_analysis,
        ),
        make_structured_tool(
            name="pollen_forecast",
            description=ATMOSPHERIC_DESCRIPTIONS["pollen_forecast"],
            args_schema=LatLonInput,
            fn=pollen_forecast,
        ),
        make_structured_tool(
            name="uv_index_forecast",
            description=ATMOSPHERIC_DESCRIPTIONS["uv_index_forecast"],
            args_schema=LatLonInput,
            fn=uv_index_forecast,
        ),
    ]
