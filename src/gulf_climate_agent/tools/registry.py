from __future__ import annotations

from dataclasses import dataclass

from gulf_climate_agent.core.langchain_compat import BaseTool

from gulf_climate_agent.config.settings import Settings
from gulf_climate_agent.core.artifacts import ArtifactStore
from gulf_climate_agent.core.http import JsonHttpClient
from gulf_climate_agent.infra.bioclip_service import BioClipClassifier
from gulf_climate_agent.infra.bird_classifier import BirdCallClassifier
from gulf_climate_agent.infra.carbon_service import CarbonFootprintService
from gulf_climate_agent.infra.earth_engine_session import EarthEngineSession
from gulf_climate_agent.infra.open_meteo_client import OpenMeteoService
from gulf_climate_agent.infra.openai_client import OpenAIResponsesClient
from gulf_climate_agent.infra.satellite_service import Sentinel2Service
from gulf_climate_agent.infra.tavily_client import TavilySearchClient
from gulf_climate_agent.tools.atmospheric_tools import build_atmospheric_tools
from gulf_climate_agent.tools.base import ToolServices
from gulf_climate_agent.tools.biodiversity_tools import build_biodiversity_tools
from gulf_climate_agent.tools.remote_sensing_tools import build_remote_sensing_tools
from gulf_climate_agent.tools.retrieval_tools import build_retrieval_tools
from gulf_climate_agent.tools.sustainability_tools import build_sustainability_tools
from gulf_climate_agent.tools.weather_tools import build_weather_tools


@dataclass(slots=True)
class ToolRegistry:
    services: ToolServices
    tools: list[BaseTool]

    @property
    def tool_map(self) -> dict[str, BaseTool]:
        return {tool.name: tool for tool in self.tools}

    def select(self, names: list[str]) -> list[BaseTool]:
        mapping = self.tool_map
        return [mapping[name] for name in names if name in mapping]

    def names(self) -> list[str]:
        return [tool.name for tool in self.tools]


def build_tool_registry(settings: Settings | None = None) -> ToolRegistry:
    settings = settings or Settings.load()
    http = JsonHttpClient(timeout=settings.gca_http_timeout, retries=settings.gca_http_retries)
    artifacts = ArtifactStore(settings.artifacts_path)
    ee_session = EarthEngineSession(settings)
    services = ToolServices(
        settings=settings,
        artifacts=artifacts,
        http=http,
        satellite=Sentinel2Service(settings=settings, artifacts=artifacts, http=http, ee_session=ee_session),
        openai=OpenAIResponsesClient(settings),
        tavily=TavilySearchClient(settings, http),
        birds=BirdCallClassifier(settings),
        bioclip=BioClipClassifier(settings),
        carbon=CarbonFootprintService(settings),
        open_meteo=OpenMeteoService(settings, http),
    )
    tools: list[BaseTool] = []
    tools.extend(build_remote_sensing_tools(services))
    tools.extend(build_biodiversity_tools(services))
    tools.extend(build_retrieval_tools(services))
    tools.extend(build_sustainability_tools(services))
    tools.extend(build_atmospheric_tools(services))
    tools.extend(build_weather_tools(services))
    return ToolRegistry(services=services, tools=tools)
