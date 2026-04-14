from gulf_climate_agent.controller.tool_controller import ToolController


def test_controller_injects_geocode_for_city_weather_query() -> None:
    controller = ToolController()
    route = controller.decide("Analyze rainfall extremes for Doha between 2024-01-01 and 2024-12-31")
    assert "geocode_mapping" in route.enabled_tools
    assert "rain_analysis" in route.enabled_tools


def test_controller_routes_remote_sensing() -> None:
    controller = ToolController()
    route = controller.decide("Compare desertification signals near 24.45,54.38 between 2020-03-15 and 2025-03-15")
    assert "get_satellite_image" in route.enabled_tools
    assert "desertification_analysis" in route.enabled_tools
