from __future__ import annotations

from gulf_climate_agent.contracts.sustainability import CarbonFootprintInput, CarbonFootprintOutput
from gulf_climate_agent.tools.base import ToolServices, build_meta, dump_model, make_structured_tool


SUSTAINABILITY_DESCRIPTIONS = {
    "carbon_footprint_calculation": "Estimate annual carbon emissions for a GCC country and industry given year and revenue.",
}


def build_sustainability_tools(services: ToolServices):
    carbon = services.carbon

    def carbon_footprint_calculation(country: str, industry: str, year: int, revenue: float):
        payload = CarbonFootprintInput(country=country, industry=industry, year=year, revenue=revenue)
        result = carbon.estimate(country=payload.country, industry=payload.industry, year=payload.year, revenue=payload.revenue)
        output = CarbonFootprintOutput(
            meta=build_meta(provider="gcc_exiobase_estimator", source="exiobase_style_spend_factors", units={"tCO2e": "metric_tons"}),
            tCO2e=result["tCO2e"],
            scopes=result["scopes"],
            methodology=result["methodology"],
        )
        return dump_model(output)

    return [
        make_structured_tool(name="carbon_footprint_calculation", description=SUSTAINABILITY_DESCRIPTIONS["carbon_footprint_calculation"], args_schema=CarbonFootprintInput, fn=carbon_footprint_calculation),
    ]
