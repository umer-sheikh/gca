from __future__ import annotations

from gulf_climate_agent.agent.runtime import LangChainGCAAgent
from gulf_climate_agent.config.settings import Settings
from gulf_climate_agent.controller.tool_controller import ToolController
from gulf_climate_agent.tools.registry import build_tool_registry


def build_default_agent(settings: Settings | None = None) -> LangChainGCAAgent:
    settings = settings or Settings.load()
    registry = build_tool_registry(settings)
    controller = ToolController()
    return LangChainGCAAgent(settings=settings, registry=registry, controller=controller)
