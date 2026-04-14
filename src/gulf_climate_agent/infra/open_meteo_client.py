from __future__ import annotations

import statistics
from typing import Any

from gulf_climate_agent.config.settings import Settings
from gulf_climate_agent.core.http import JsonHttpClient
from gulf_climate_agent.core.normalization import infer_trend, summarize_numeric, to_time_series


class OpenMeteoService:
    AIR_HOURLY_DEFAULT = [
        "european_aqi",
        "pm2_5",
        "pm10",
        "nitrogen_dioxide",
        "ozone",
        "sulphur_dioxide",
        "carbon_monoxide",
        "dust",
    ]

    POLLEN_HOURLY = [
        "alder_pollen",
        "birch_pollen",
        "grass_pollen",
        "mugwort_pollen",
        "olive_pollen",
        "ragweed_pollen",
    ]

    WEATHER_HOURLY_DEFAULT = [
        "temperature_2m",
        "relative_humidity_2m",
        "wind_speed_10m",
        "wind_direction_10m",
        "precipitation",
        "rain",
        "surface_pressure",
        "cloud_cover",
    ]

    WEATHER_DAILY_DEFAULT = [
        "temperature_2m_max",
        "temperature_2m_min",
        "temperature_2m_mean",
        "precipitation_sum",
        "rain_sum",
        "wind_speed_10m_max",
    ]

    def __init__(self, settings: Settings, http: JsonHttpClient) -> None:
        self.settings = settings
        self.http = http

    def _get(self, url: str, params: dict[str, Any], *, with_key: bool = True) -> dict[str, Any]:
        query = dict(params)
        if with_key and self.settings.open_meteo.api_key:
            query["apikey"] = self.settings.open_meteo.api_key
        return self.http.get_json(url, params=query)

    def geocode_mapping(self, *, region: str) -> dict[str, Any]:
        data = self._get(
            self.settings.open_meteo.geocoding_url,
            {"name": region, "count": 3, "language": "en", "format": "json"},
            with_key=False,
        )
        results = data.get("results") or []
        if not results:
            raise ValueError(f"No geocoding result found for region={region}")
        top = results[0]
        return {
            "lat": float(top["latitude"]),
            "lon": float(top["longitude"]),
            "metadata": {
                "query": region,
                "name": top.get("name"),
                "country": top.get("country"),
                "admin1": top.get("admin1"),
                "timezone": top.get("timezone"),
                "raw_top_result": top,
            },
        }

    def aqi_inquiry(self, *, lat: float, lon: float, date: str) -> dict[str, Any]:
        data = self._get(
            self.settings.open_meteo.air_quality_url,
            {
                "latitude": lat,
                "longitude": lon,
                "start_date": date,
                "end_date": date,
                "hourly": ",".join(self.AIR_HOURLY_DEFAULT),
                "timezone": "auto",
            },
        )
        hourly = data.get("hourly", {})
        aqi = summarize_numeric(hourly.get("european_aqi", []) or [])
        pollutants = {key: summarize_numeric(hourly.get(key, []) or []) for key in self.AIR_HOURLY_DEFAULT if key != "european_aqi"}
        return {"aqi": aqi, "pollutants": pollutants, "timezone": data.get("timezone"), "units": data.get("hourly_units", {})}

    def aqi_prediction(self, *, lat: float, lon: float, horizon: int) -> dict[str, Any]:
        data = self._get(
            self.settings.open_meteo.air_quality_url,
            {
                "latitude": lat,
                "longitude": lon,
                "forecast_days": int(horizon),
                "hourly": "european_aqi,pm2_5,pm10",
                "timezone": "auto",
            },
        )
        hourly = data.get("hourly", {})
        return {
            "aqi_time_series": to_time_series(
                hourly.get("time", []) or [],
                {
                    "european_aqi": hourly.get("european_aqi", []) or [],
                    "pm2_5": hourly.get("pm2_5", []) or [],
                    "pm10": hourly.get("pm10", []) or [],
                },
                data.get("hourly_units", {}),
            ),
            "timezone": data.get("timezone"),
        }

    def aqi_analysis(self, *, lat: float, lon: float, start: str, end: str) -> dict[str, Any]:
        data = self._get(
            self.settings.open_meteo.air_quality_url,
            {
                "latitude": lat,
                "longitude": lon,
                "start_date": start,
                "end_date": end,
                "hourly": "european_aqi,pm2_5,pm10",
                "timezone": "auto",
            },
        )
        hourly = data.get("hourly", {})
        aqi = [float(v) for v in (hourly.get("european_aqi", []) or []) if v is not None]
        return {
            "stats": {
                "mean_european_aqi": float(statistics.fmean(aqi)) if aqi else None,
                "max_european_aqi": float(max(aqi)) if aqi else None,
                "hours": len(aqi),
            },
            "trend": infer_trend(aqi),
            "exceedances": {
                ">60": sum(1 for v in aqi if v > 60),
                ">80": sum(1 for v in aqi if v > 80),
                ">100": sum(1 for v in aqi if v > 100),
            },
            "timezone": data.get("timezone"),
            "units": data.get("hourly_units", {}),
        }

    def pollen_forecast(self, *, lat: float, lon: float) -> dict[str, Any]:
        data = self._get(
            self.settings.open_meteo.air_quality_url,
            {
                "latitude": lat,
                "longitude": lon,
                "forecast_days": self.settings.default_pollen_forecast_days,
                "hourly": ",".join(self.POLLEN_HOURLY),
                "timezone": "auto",
            },
        )
        hourly = data.get("hourly", {})
        return {
            "pollen_levels": to_time_series(
                hourly.get("time", []) or [],
                {key: hourly.get(key, []) or [] for key in self.POLLEN_HOURLY},
                data.get("hourly_units", {}),
            ),
            "timezone": data.get("timezone"),
        }

    def uv_index_forecast(self, *, lat: float, lon: float) -> dict[str, Any]:
        data = self._get(
            self.settings.open_meteo.weather_url,
            {
                "latitude": lat,
                "longitude": lon,
                "forecast_days": self.settings.default_uv_forecast_days,
                "hourly": "uv_index,uv_index_clear_sky",
                "daily": "uv_index_max,uv_index_clear_sky_max",
                "timezone": "auto",
            },
        )
        hourly = data.get("hourly", {})
        return {
            "uv_time_series": to_time_series(
                hourly.get("time", []) or [],
                {
                    "uv_index": hourly.get("uv_index", []) or [],
                    "uv_index_clear_sky": hourly.get("uv_index_clear_sky", []) or [],
                },
                data.get("hourly_units", {}),
            ),
            "timezone": data.get("timezone"),
            "daily": data.get("daily", {}),
            "daily_units": data.get("daily_units", {}),
        }

    def weather_inquiry(self, *, lat: float, lon: float, date: str) -> dict[str, Any]:
        data = self._get(
            self.settings.open_meteo.archive_url,
            {
                "latitude": lat,
                "longitude": lon,
                "start_date": date,
                "end_date": date,
                "hourly": ",".join(self.WEATHER_HOURLY_DEFAULT),
                "daily": ",".join(self.WEATHER_DAILY_DEFAULT),
                "timezone": "auto",
            },
        )
        return {"weather": data}

    def weather_forecast(self, *, lat: float, lon: float, days: int) -> dict[str, Any]:
        data = self._get(
            self.settings.open_meteo.weather_url,
            {
                "latitude": lat,
                "longitude": lon,
                "forecast_days": int(days),
                "hourly": ",".join(self.WEATHER_HOURLY_DEFAULT),
                "daily": ",".join(self.WEATHER_DAILY_DEFAULT),
                "timezone": "auto",
            },
        )
        return {"forecast_series": data}

    def weather_analysis(self, *, lat: float, lon: float, start: str, end: str) -> dict[str, Any]:
        data = self._get(
            self.settings.open_meteo.archive_url,
            {
                "latitude": lat,
                "longitude": lon,
                "start_date": start,
                "end_date": end,
                "daily": "temperature_2m_mean,temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max",
                "timezone": "auto",
            },
        )
        daily = data.get("daily", {})
        temps = [v for v in (daily.get("temperature_2m_mean") or []) if v is not None]
        precip = [v for v in (daily.get("precipitation_sum") or []) if v is not None]
        summary = {
            "days": len(daily.get("time", []) or []),
            "temp_mean_c": float(statistics.fmean(temps)) if temps else None,
            "temp_max_c": float(max(daily.get("temperature_2m_max") or [0])) if daily.get("temperature_2m_max") else None,
            "temp_min_c": float(min(daily.get("temperature_2m_min") or [0])) if daily.get("temperature_2m_min") else None,
            "precip_total_mm": float(sum(precip)) if precip else 0.0,
        }
        anomalies = {
            "temp_mean_trend": infer_trend(temps),
            "precip_trend": infer_trend(precip),
            "baseline_note": "This implementation uses first-vs-last directional summaries instead of a climatology archive.",
        }
        return {"stats": summary, "anomalies": anomalies, "timezone": data.get("timezone"), "units": data.get("daily_units", {})}

    def rain_inquiry(self, *, lat: float, lon: float, date: str) -> dict[str, Any]:
        data = self._get(
            self.settings.open_meteo.archive_url,
            {
                "latitude": lat,
                "longitude": lon,
                "start_date": date,
                "end_date": date,
                "daily": "precipitation_sum",
                "timezone": "auto",
            },
        )
        daily = data.get("daily", {})
        series = daily.get("precipitation_sum", []) or []
        return {"precip_mm": float(series[0]) if series else None, "unit": (data.get("daily_units", {}) or {}).get("precipitation_sum", "mm")}

    def rain_prediction(self, *, lat: float, lon: float, horizon: int) -> dict[str, Any]:
        data = self._get(
            self.settings.open_meteo.weather_url,
            {
                "latitude": lat,
                "longitude": lon,
                "forecast_days": int(horizon),
                "daily": "precipitation_sum,rain_sum",
                "timezone": "auto",
            },
        )
        daily = data.get("daily", {})
        return {
            "precip_series": to_time_series(
                daily.get("time", []) or [],
                {
                    "precipitation_sum": daily.get("precipitation_sum", []) or [],
                    "rain_sum": daily.get("rain_sum", []) or [],
                },
                data.get("daily_units", {}),
            )
        }

    def rain_analysis(self, *, lat: float, lon: float, start: str, end: str) -> dict[str, Any]:
        data = self._get(
            self.settings.open_meteo.archive_url,
            {
                "latitude": lat,
                "longitude": lon,
                "start_date": start,
                "end_date": end,
                "daily": "precipitation_sum,rain_sum",
                "timezone": "auto",
            },
        )
        daily = data.get("daily", {})
        times = daily.get("time", []) or []
        precip = [float(v) for v in (daily.get("precipitation_sum") or []) if v is not None]
        events: list[dict[str, Any]] = []
        for t, v in zip(times, daily.get("precipitation_sum", []) or []):
            if v is None:
                continue
            value = float(v)
            if value >= 25:
                events.append({"date": t, "precip_mm": value, "label": "very_heavy"})
            elif value >= 10:
                events.append({"date": t, "precip_mm": value, "label": "heavy"})
        return {
            "stats": {
                "total_precip_mm": float(sum(precip)) if precip else 0.0,
                "max_daily_precip_mm": float(max(precip)) if precip else 0.0,
                "days_with_precip_ge_10mm": sum(1 for x in precip if x >= 10.0),
                "days_with_precip_ge_25mm": sum(1 for x in precip if x >= 25.0),
                "n_days": len(times),
            },
            "events": events,
            "units": data.get("daily_units", {}),
        }

    def river_discharge_check(self, *, lat: float, lon: float, date: str) -> dict[str, Any]:
        data = self._get(
            self.settings.open_meteo.flood_url,
            {
                "latitude": lat,
                "longitude": lon,
                "start_date": date,
                "end_date": date,
                "daily": "river_discharge",
                "cell_selection": "nearest",
                "timezone": "GMT",
            },
        )
        daily = data.get("daily", {})
        discharge = daily.get("river_discharge", []) or []
        return {
            "discharge_m3_s": float(discharge[0]) if discharge else None,
            "unit": (data.get("daily_units", {}) or {}).get("river_discharge", "m3/s"),
            "note": "Nearest river cell may be offset from the requested point because the product is gridded.",
        }
