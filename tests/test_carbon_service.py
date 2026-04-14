from gulf_climate_agent.config.settings import Settings
from gulf_climate_agent.infra.carbon_service import CarbonFootprintService


def test_carbon_service_estimate() -> None:
    settings = Settings()
    service = CarbonFootprintService(settings)
    result = service.estimate(country="United Arab Emirates", industry="Construction", year=2024, revenue=1000.0)
    assert result["tCO2e"] > 0
    assert set(result["scopes"].keys()) == {"scope1", "scope2", "scope3"}
