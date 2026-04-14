from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from gulf_climate_agent.core.langchain_compat import StructuredTool

from gulf_climate_agent.config.settings import Settings
from gulf_climate_agent.contracts.base import OutputMeta
from gulf_climate_agent.core.artifacts import ArtifactStore
from gulf_climate_agent.core.http import JsonHttpClient
from gulf_climate_agent.core.serialization import to_jsonable
from gulf_climate_agent.infra.bioclip_service import BioClipClassifier
from gulf_climate_agent.infra.bird_classifier import BirdCallClassifier
from gulf_climate_agent.infra.carbon_service import CarbonFootprintService
from gulf_climate_agent.infra.open_meteo_client import OpenMeteoService
from gulf_climate_agent.infra.openai_client import OpenAIResponsesClient
from gulf_climate_agent.infra.satellite_service import Sentinel2Service
from gulf_climate_agent.infra.tavily_client import TavilySearchClient


@dataclass(slots=True)
class ToolServices:
    settings: Settings
    artifacts: ArtifactStore
    http: JsonHttpClient
    satellite: Sentinel2Service
    openai: OpenAIResponsesClient
    tavily: TavilySearchClient
    birds: BirdCallClassifier
    bioclip: BioClipClassifier
    carbon: CarbonFootprintService
    open_meteo: OpenMeteoService


def build_meta(*, provider: str, source: str | None = None, units: dict[str, str] | None = None, warnings: list[str] | None = None, location: dict[str, Any] | None = None, timestamps: dict[str, str] | None = None) -> OutputMeta:
    return OutputMeta(
        provider=provider,
        source=source,
        units=units or {},
        warnings=warnings or [],
        location=location,
        timestamps=timestamps or {},
    )


def make_structured_tool(*, name: str, description: str, args_schema: type, fn: Callable[..., Any]) -> StructuredTool:
    return StructuredTool.from_function(
        name=name,
        description=description,
        args_schema=args_schema,
        func=fn,
        return_direct=False,
    )


def dump_model(model: Any) -> dict[str, Any]:
    return to_jsonable(model)
