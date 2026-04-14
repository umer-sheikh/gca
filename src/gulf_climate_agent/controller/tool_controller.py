from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum


class ToolDomain(str, Enum):
    REMOTE_SENSING = "remote_sensing"
    BIODIVERSITY = "biodiversity"
    WEB = "web_retrieval"
    CARBON = "carbon"
    AIR = "air_quality"
    WEATHER = "weather_hydrology"


DOMAIN_TO_TOOLS: dict[ToolDomain, list[str]] = {
    ToolDomain.REMOTE_SENSING: [
        "get_satellite_image",
        "calculate_ndvi",
        "calculate_ndwi",
        "desertification_analysis",
    ],
    ToolDomain.BIODIVERSITY: ["detect_bird", "detect_species"],
    ToolDomain.WEB: ["online_search", "summarize"],
    ToolDomain.CARBON: ["carbon_footprint_calculation"],
    ToolDomain.AIR: ["aqi_inquiry", "aqi_prediction", "aqi_analysis", "pollen_forecast", "uv_index_forecast"],
    ToolDomain.WEATHER: [
        "geocode_mapping",
        "weather_inquiry",
        "weather_forecast",
        "weather_analysis",
        "rain_inquiry",
        "rain_prediction",
        "rain_analysis",
        "river_discharge_check",
    ],
}


DOMAIN_KEYWORDS: dict[ToolDomain, tuple[str, ...]] = {
    ToolDomain.REMOTE_SENSING: (
        "satellite", "imagery", "image", "ndvi", "ndwi", "desertification", "desert",
        "geotiff", "land surface", "vegetation", "shoreline", "remote sensing",
    ),
    ToolDomain.BIODIVERSITY: (
        "bird", "species", "biodiversity", "audio", "call", "animal", "plant", "bioclip",
    ),
    ToolDomain.WEB: (
        "policy", "report", "paper", "news", "search", "summarize", "summary", "document",
        "framework", "guideline", "advisory",
    ),
    ToolDomain.CARBON: (
        "carbon", "emission", "footprint", "scope 1", "scope 2", "scope 3", "tco2e", "revenue", "industry",
    ),
    ToolDomain.AIR: (
        "aqi", "pm10", "pm2.5", "pm2_5", "pollution", "air quality", "dust", "ozone", "uv", "pollen",
    ),
    ToolDomain.WEATHER: (
        "weather", "temperature", "rain", "precip", "hydrology", "flood", "river", "discharge", "wind", "forecast",
    ),
}


GULF_LOCATION_MARKERS = (
    "uae", "united arab emirates", "abu dhabi", "dubai", "riyadh", "jeddah", "saudi",
    "qatar", "doha", "oman", "muscat", "bahrain", "manama", "kuwait", "kuwait city",
)


@dataclass(slots=True)
class RouteDecision:
    dominant_intent: str
    enabled_tools: list[str]
    domain_scores: dict[str, float] = field(default_factory=dict)
    rationale: list[str] = field(default_factory=list)


class ToolController:
    coordinate_pattern = re.compile(r"-?\d{1,3}\.\d+\s*,\s*-?\d{1,3}\.\d+")

    def _contains_coordinates(self, query: str) -> bool:
        return bool(self.coordinate_pattern.search(query))

    def decide(self, query: str) -> RouteDecision:
        lower = query.lower()
        scores: dict[ToolDomain, float] = defaultdict(float)
        rationale: list[str] = []

        for domain, terms in DOMAIN_KEYWORDS.items():
            for term in terms:
                if term in lower:
                    scores[domain] += 1.0

        if not scores:
            scores[ToolDomain.WEB] = 0.5
            rationale.append("no strong domain marker found; defaulting to retrieval/summarization")

        ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
        selected_domains = [domain for domain, score in ranked if score > 0][:2] or [ToolDomain.WEB]
        enabled: list[str] = []
        for domain in selected_domains:
            enabled.extend(DOMAIN_TO_TOOLS[domain])

        if any(marker in lower for marker in GULF_LOCATION_MARKERS) and not self._contains_coordinates(query):
            if any(domain in selected_domains for domain in (ToolDomain.WEATHER, ToolDomain.AIR, ToolDomain.REMOTE_SENSING)):
                if "geocode_mapping" not in enabled:
                    enabled.insert(0, "geocode_mapping")
                    rationale.append("location-like marker detected without explicit coordinates; geocoder injected")

        if any(token in lower for token in ("summarize", "summary", "report", "explain")) and "summarize" not in enabled:
            enabled.append("summarize")

        if any(token in lower for token in ("search", "policy", "news", "report")) and "online_search" not in enabled:
            enabled.append("online_search")

        enabled = list(dict.fromkeys(enabled))
        dominant = selected_domains[0].value if selected_domains else ToolDomain.WEB.value
        domain_scores = {domain.value: float(score) for domain, score in ranked}
        return RouteDecision(dominant_intent=dominant, enabled_tools=enabled, domain_scores=domain_scores, rationale=rationale)
