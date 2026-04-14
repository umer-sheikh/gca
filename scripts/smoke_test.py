from __future__ import annotations

import json

from gulf_climate_agent.config.settings import Settings
from gulf_climate_agent.controller.tool_controller import ToolController
from gulf_climate_agent.infra.carbon_service import CarbonFootprintService
from gulf_climate_agent.tools.registry import build_tool_registry


def main() -> None:
    settings = Settings.load()
    registry = build_tool_registry(settings)
    controller = ToolController()
    route = controller.decide("Analyze rainfall extremes for Doha between 2024-01-01 and 2024-12-31")
    carbon = CarbonFootprintService(settings)
    estimate = carbon.estimate(country="United Arab Emirates", industry="Construction", year=2024, revenue=12_500_000)
    print(json.dumps({
        "n_tools": len(registry.names()),
        "route": route.enabled_tools,
        "carbon_estimate": estimate,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
