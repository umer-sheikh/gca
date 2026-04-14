from __future__ import annotations

from gulf_climate_agent.config.settings import Settings
from gulf_climate_agent.infra.carbon_catalog import build_ef_table_gcc, estimate_emissions_exiobase_single


class CarbonFootprintService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.ef_table = build_ef_table_gcc(price_year=settings.carbon.ef_year, currency=settings.carbon.ef_currency)

    def estimate(self, *, country: str, industry: str, year: int, revenue: float) -> dict:
        result = estimate_emissions_exiobase_single(
            country=country,
            sector=industry,
            revenue=revenue,
            currency=self.settings.carbon.default_currency,
            rev_price_year=year,
            ef_table=self.ef_table,
            ef_price_year=self.settings.carbon.ef_year,
            ef_currency=self.settings.carbon.ef_currency,
            fx_to_ef_currency=self.settings.carbon.fx_to_ef,
            deflator_to_ef_year=self.settings.carbon.deflator_to_ef_year,
        )
        return {
            "tCO2e": float(result["total_tCO2e"]),
            "scopes": {
                "scope1": float(result["scope1_tCO2e"]),
                "scope2": float(result["scope2_tCO2e"]),
                "scope3": float(result["scope3_tCO2e"]),
            },
            "methodology": {
                "ef_currency": result["ef_currency"],
                "ef_price_year": result["ef_price_year"],
                "ef_note": result["ef_note"],
                "revenue_currency": result["revenue_currency"],
                "rev_price_year": result["rev_price_year"],
                "revenue_in_ef_units": result["revenue_in_ef_units"],
                "ef_kg_per_currency": result["ef_kg_per_currency"],
            },
        }
