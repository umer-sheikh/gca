from __future__ import annotations

from gulf_climate_agent.contracts.base import TimeSeries
from gulf_climate_agent.contracts.weather import GeocodeMappingInput, GeocodeMappingOutput, LatLonDateInput, LatLonDaysInput, LatLonHorizonInput, LatLonRangeInput, RainAnalysisOutput, RainInquiryOutput, RainPredictionOutput, RiverDischargeOutput, WeatherAnalysisOutput, WeatherForecastOutput, WeatherInquiryOutput
from gulf_climate_agent.tools.base import ToolServices, build_meta, dump_model, make_structured_tool


WEATHER_DESCRIPTIONS = {
    "geocode_mapping": "Resolve a region or city name to coordinates for downstream tool calls.",
    "weather_inquiry": "Return historical weather variables for a location and date.",
    "weather_forecast": "Return weather forecast for the next n days.",
    "weather_analysis": "Compute summary statistics and anomalies over a date range.",
    "rain_inquiry": "Return precipitation for a location and date.",
    "rain_prediction": "Forecast precipitation for a location over a specified horizon.",
    "rain_analysis": "Summarize rainfall patterns and extremes over a date range.",
    "river_discharge_check": "Return simulated river discharge for the nearest river grid cell at a date.",
}


def build_weather_tools(services: ToolServices):
    open_meteo = services.open_meteo

    def geocode_mapping(region: str):
        payload = GeocodeMappingInput(region=region)
        result = open_meteo.geocode_mapping(region=payload.region)
        output = GeocodeMappingOutput(
            meta=build_meta(provider="open-meteo", source=services.settings.open_meteo.geocoding_url, location={"region": payload.region}),
            lat=result["lat"],
            lon=result["lon"],
            metadata=result["metadata"],
        )
        return dump_model(output)

    def weather_inquiry(lat: float, lon: float, date: str):
        payload = LatLonDateInput(lat=lat, lon=lon, date=date)
        result = open_meteo.weather_inquiry(lat=payload.lat, lon=payload.lon, date=payload.date)
        daily_units = (result.get("weather", {}).get("daily_units") or {})
        hourly_units = (result.get("weather", {}).get("hourly_units") or {})
        output = WeatherInquiryOutput(
            meta=build_meta(provider="open-meteo", source=services.settings.open_meteo.archive_url, units={**hourly_units, **daily_units}, location={"lat": payload.lat, "lon": payload.lon}, timestamps={"date": payload.date}),
            weather=result["weather"],
        )
        return dump_model(output)

    def weather_forecast(lat: float, lon: float, days: int):
        payload = LatLonDaysInput(lat=lat, lon=lon, days=days)
        result = open_meteo.weather_forecast(lat=payload.lat, lon=payload.lon, days=payload.days)
        daily_units = (result.get("forecast_series", {}).get("daily_units") or {})
        hourly_units = (result.get("forecast_series", {}).get("hourly_units") or {})
        output = WeatherForecastOutput(
            meta=build_meta(provider="open-meteo", source=services.settings.open_meteo.weather_url, units={**hourly_units, **daily_units}, location={"lat": payload.lat, "lon": payload.lon}),
            forecast_series=result["forecast_series"],
        )
        return dump_model(output)

    def weather_analysis(lat: float, lon: float, start: str, end: str):
        payload = LatLonRangeInput(lat=lat, lon=lon, start=start, end=end)
        result = open_meteo.weather_analysis(lat=payload.lat, lon=payload.lon, start=payload.start, end=payload.end)
        output = WeatherAnalysisOutput(
            meta=build_meta(provider="open-meteo", source=services.settings.open_meteo.archive_url, units=result.get("units", {}), location={"lat": payload.lat, "lon": payload.lon}, timestamps={"start": payload.start, "end": payload.end}),
            stats=result["stats"],
            anomalies=result["anomalies"],
        )
        return dump_model(output)

    def rain_inquiry(lat: float, lon: float, date: str):
        payload = LatLonDateInput(lat=lat, lon=lon, date=date)
        result = open_meteo.rain_inquiry(lat=payload.lat, lon=payload.lon, date=payload.date)
        output = RainInquiryOutput(
            meta=build_meta(provider="open-meteo", source=services.settings.open_meteo.archive_url, units={"precip_mm": result.get("unit", "mm")}, location={"lat": payload.lat, "lon": payload.lon}, timestamps={"date": payload.date}),
            precip_mm=result["precip_mm"],
        )
        return dump_model(output)

    def rain_prediction(lat: float, lon: float, horizon: int):
        payload = LatLonHorizonInput(lat=lat, lon=lon, horizon=horizon)
        result = open_meteo.rain_prediction(lat=payload.lat, lon=payload.lon, horizon=payload.horizon)
        output = RainPredictionOutput(
            meta=build_meta(provider="open-meteo", source=services.settings.open_meteo.weather_url, units=result["precip_series"].get("units", {}), location={"lat": payload.lat, "lon": payload.lon}),
            precip_series=TimeSeries(**result["precip_series"]),
        )
        return dump_model(output)

    def rain_analysis(lat: float, lon: float, start: str, end: str):
        payload = LatLonRangeInput(lat=lat, lon=lon, start=start, end=end)
        result = open_meteo.rain_analysis(lat=payload.lat, lon=payload.lon, start=payload.start, end=payload.end)
        output = RainAnalysisOutput(
            meta=build_meta(provider="open-meteo", source=services.settings.open_meteo.archive_url, units=result.get("units", {}), location={"lat": payload.lat, "lon": payload.lon}, timestamps={"start": payload.start, "end": payload.end}),
            stats=result["stats"],
            events=result["events"],
        )
        return dump_model(output)

    def river_discharge_check(lat: float, lon: float, date: str):
        payload = LatLonDateInput(lat=lat, lon=lon, date=date)
        result = open_meteo.river_discharge_check(lat=payload.lat, lon=payload.lon, date=payload.date)
        output = RiverDischargeOutput(
            meta=build_meta(provider="open-meteo", source=services.settings.open_meteo.flood_url, units={"discharge_m3_s": result.get("unit", "m3/s")}, warnings=[result.get("note")] if result.get("note") else [], location={"lat": payload.lat, "lon": payload.lon}, timestamps={"date": payload.date}),
            discharge_m3_s=result["discharge_m3_s"],
        )
        return dump_model(output)

    return [
        make_structured_tool(name="geocode_mapping", description=WEATHER_DESCRIPTIONS["geocode_mapping"], args_schema=GeocodeMappingInput, fn=geocode_mapping),
        make_structured_tool(name="weather_inquiry", description=WEATHER_DESCRIPTIONS["weather_inquiry"], args_schema=LatLonDateInput, fn=weather_inquiry),
        make_structured_tool(name="weather_forecast", description=WEATHER_DESCRIPTIONS["weather_forecast"], args_schema=LatLonDaysInput, fn=weather_forecast),
        make_structured_tool(name="weather_analysis", description=WEATHER_DESCRIPTIONS["weather_analysis"], args_schema=LatLonRangeInput, fn=weather_analysis),
        make_structured_tool(name="rain_inquiry", description=WEATHER_DESCRIPTIONS["rain_inquiry"], args_schema=LatLonDateInput, fn=rain_inquiry),
        make_structured_tool(name="rain_prediction", description=WEATHER_DESCRIPTIONS["rain_prediction"], args_schema=LatLonHorizonInput, fn=rain_prediction),
        make_structured_tool(name="rain_analysis", description=WEATHER_DESCRIPTIONS["rain_analysis"], args_schema=LatLonRangeInput, fn=rain_analysis),
        make_structured_tool(name="river_discharge_check", description=WEATHER_DESCRIPTIONS["river_discharge_check"], args_schema=LatLonDateInput, fn=river_discharge_check),
    ]
