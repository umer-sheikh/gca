from __future__ import annotations

from typing import Dict, List, Optional, Union

SUPPORTED_SECTORS_GCC = [
    "Oil & Gas Extraction",
    "Refining & Petrochemicals",
    "Electricity & Steam Generation",
    "Water Desalination & Supply",
    "Cement & Concrete",
    "Basic Iron & Steel",
    "Aluminium Smelting",
    "Chemicals (ex-Petrochemicals)",
    "Plastics & Rubber",
    "Glass & Ceramics",
    "Mining & Quarrying (non-energy)",
    "Food & Beverage Manufacturing",
    "Textiles & Apparel",
    "Paper & Printing",
    "Construction",
    "Road Freight & Logistics",
    "Aviation Services",
    "Maritime Transport",
    "Telecommunications",
    "IT & Data Centers",
    "Retail & Wholesale",
    "Real Estate & Facilities Mgmt",
    "Hospitality (Hotels & Restaurants)",
    "Healthcare",
    "Education",
    "Waste Management",
    "Financial & Professional Services",
    "Agriculture & Livestock",
]

SECTOR_SYNONYMS = {
    "oil and gas": "Oil & Gas Extraction",
    "upstream": "Oil & Gas Extraction",
    "refining": "Refining & Petrochemicals",
    "petrochemical": "Refining & Petrochemicals",
    "power generation": "Electricity & Steam Generation",
    "electricity": "Electricity & Steam Generation",
    "desalination": "Water Desalination & Supply",
    "cement": "Cement & Concrete",
    "steel": "Basic Iron & Steel",
    "aluminum": "Aluminium Smelting",
    "aluminium": "Aluminium Smelting",
    "chemicals": "Chemicals (ex-Petrochemicals)",
    "rubber": "Plastics & Rubber",
    "plastics": "Plastics & Rubber",
    "glass": "Glass & Ceramics",
    "ceramics": "Glass & Ceramics",
    "mining": "Mining & Quarrying (non-energy)",
    "f&b manufacturing": "Food & Beverage Manufacturing",
    "food manufacturing": "Food & Beverage Manufacturing",
    "textiles": "Textiles & Apparel",
    "printing": "Paper & Printing",
    "construction industry": "Construction",
    "logistics": "Road Freight & Logistics",
    "road freight": "Road Freight & Logistics",
    "trucking": "Road Freight & Logistics",
    "aviation": "Aviation Services",
    "airlines": "Aviation Services",
    "shipping": "Maritime Transport",
    "ports": "Maritime Transport",
    "telco": "Telecommunications",
    "data center": "IT & Data Centers",
    "datacenter": "IT & Data Centers",
    "retail": "Retail & Wholesale",
    "wholesale": "Retail & Wholesale",
    "real estate": "Real Estate & Facilities Mgmt",
    "facilities": "Real Estate & Facilities Mgmt",
    "hotels": "Hospitality (Hotels & Restaurants)",
    "restaurants": "Hospitality (Hotels & Restaurants)",
    "hospitality": "Hospitality (Hotels & Restaurants)",
    "healthcare": "Healthcare",
    "education": "Education",
    "waste": "Waste Management",
    "financial services": "Financial & Professional Services",
    "banking": "Financial & Professional Services",
    "agriculture": "Agriculture & Livestock",
    "livestock": "Agriculture & Livestock",
}

SECTOR_SCOPE_SHARES_GCC = {
    "Oil & Gas Extraction":                 {"scope1": 0.65, "scope2": 0.05, "scope3": 0.30},
    "Refining & Petrochemicals":            {"scope1": 0.55, "scope2": 0.10, "scope3": 0.35},
    "Electricity & Steam Generation":       {"scope1": 0.80, "scope2": 0.05, "scope3": 0.15},
    "Water Desalination & Supply":          {"scope1": 0.20, "scope2": 0.50, "scope3": 0.30},
    "Cement & Concrete":                    {"scope1": 0.60, "scope2": 0.05, "scope3": 0.35},
    "Basic Iron & Steel":                   {"scope1": 0.30, "scope2": 0.40, "scope3": 0.30},
    "Aluminium Smelting":                   {"scope1": 0.30, "scope2": 0.40, "scope3": 0.30},
    "Chemicals (ex-Petrochemicals)":        {"scope1": 0.45, "scope2": 0.10, "scope3": 0.45},
    "Plastics & Rubber":                    {"scope1": 0.35, "scope2": 0.10, "scope3": 0.55},
    "Glass & Ceramics":                     {"scope1": 0.40, "scope2": 0.10, "scope3": 0.50},
    "Mining & Quarrying (non-energy)":      {"scope1": 0.55, "scope2": 0.10, "scope3": 0.35},
    "Food & Beverage Manufacturing":        {"scope1": 0.35, "scope2": 0.15, "scope3": 0.50},
    "Textiles & Apparel":                   {"scope1": 0.25, "scope2": 0.15, "scope3": 0.60},
    "Paper & Printing":                     {"scope1": 0.25, "scope2": 0.15, "scope3": 0.60},
    "Construction":                         {"scope1": 0.25, "scope2": 0.15, "scope3": 0.60},
    "Road Freight & Logistics":             {"scope1": 0.35, "scope2": 0.10, "scope3": 0.55},
    "Aviation Services":                    {"scope1": 0.50, "scope2": 0.05, "scope3": 0.45},
    "Maritime Transport":                   {"scope1": 0.45, "scope2": 0.05, "scope3": 0.50},
    "Telecommunications":                   {"scope1": 0.05, "scope2": 0.30, "scope3": 0.65},
    "IT & Data Centers":                    {"scope1": 0.05, "scope2": 0.45, "scope3": 0.50},
    "Retail & Wholesale":                   {"scope1": 0.05, "scope2": 0.20, "scope3": 0.75},
    "Real Estate & Facilities Mgmt":        {"scope1": 0.05, "scope2": 0.35, "scope3": 0.60},
    "Hospitality (Hotels & Restaurants)":   {"scope1": 0.10, "scope2": 0.30, "scope3": 0.60},
    "Healthcare":                           {"scope1": 0.10, "scope2": 0.30, "scope3": 0.60},
    "Education":                            {"scope1": 0.05, "scope2": 0.30, "scope3": 0.65},
    "Waste Management":                     {"scope1": 0.30, "scope2": 0.10, "scope3": 0.60},
    "Financial & Professional Services":    {"scope1": 0.02, "scope2": 0.18, "scope3": 0.80},
    "Agriculture & Livestock":              {"scope1": 0.30, "scope2": 0.10, "scope3": 0.60},
}

EF_REAL: Dict[str, float] = {
    "Oil & Gas Extraction": 1.703,
    "Refining & Petrochemicals": 2.722,
    "Cement & Concrete": 6.445,
    "Basic Iron & Steel": 1.206,
    "Aluminium Smelting": 1.880,
    "Plastics & Rubber": 0.2232,
    "Glass & Ceramics": 0.8936,
    "Food & Beverage Manufacturing": 0.5518,
    "Textiles & Apparel": 3.497,
    "Paper & Printing": 0.2789,
    "Road Freight & Logistics": 0.3692,
    "Financial & Professional Services": 0.5685,
}

PROXY_MAP: Dict[str, Dict[str, str]] = {
    "Electricity & Steam Generation": {"proxy_of": "Basic Iron & Steel", "reason": "energy-intensive industrial proxy"},
    "Water Desalination & Supply": {"proxy_of": "Glass & Ceramics", "reason": "electricity/process-heat proxy"},
    "Chemicals (ex-Petrochemicals)": {"proxy_of": "Plastics & Rubber", "reason": "closest polymer/chemical proxy"},
    "Mining & Quarrying (non-energy)": {"proxy_of": "Basic Iron & Steel", "reason": "materials/industry proxy"},
    "Construction": {"proxy_of": "Cement & Concrete", "reason": "construction materials proxy"},
    "Aviation Services": {"proxy_of": "Road Freight & Logistics", "reason": "transport services proxy"},
    "Maritime Transport": {"proxy_of": "Road Freight & Logistics", "reason": "transport services proxy"},
    "Telecommunications": {"proxy_of": "Financial & Professional Services", "reason": "services-sector proxy"},
    "IT & Data Centers": {"proxy_of": "Financial & Professional Services", "reason": "services-sector proxy"},
    "Retail & Wholesale": {"proxy_of": "Financial & Professional Services", "reason": "services-sector proxy"},
    "Real Estate & Facilities Mgmt": {"proxy_of": "Financial & Professional Services", "reason": "services-sector proxy"},
    "Hospitality (Hotels & Restaurants)": {"proxy_of": "Financial & Professional Services", "reason": "services-sector proxy"},
    "Healthcare": {"proxy_of": "Financial & Professional Services", "reason": "services-sector proxy"},
    "Education": {"proxy_of": "Financial & Professional Services", "reason": "services-sector proxy"},
    "Waste Management": {"proxy_of": "Road Freight & Logistics", "reason": "ops/vehicles-heavy proxy"},
    "Agriculture & Livestock": {"proxy_of": "Food & Beverage Manufacturing", "reason": "upstream agri proxy"},
}


def canonicalize_sector(sector: str) -> str:
    return SECTOR_SYNONYMS.get(sector.strip().lower(), sector)


def build_ef_table_gcc(price_year: int = 2019, currency: str = "EUR") -> List[Dict[str, Union[str, int, float, None]]]:
    region = "WM"
    table: List[Dict[str, Union[str, int, float, None]]] = []
    for sector in SUPPORTED_SECTORS_GCC:
        if sector in EF_REAL:
            ef = float(EF_REAL[sector])
            table.append({"region": region, "sector": sector, "price_year": price_year, "currency": currency, "ef_kg_per_currency": ef, "note": "real"})
        else:
            proxy = PROXY_MAP[sector]
            proxy_sector = proxy["proxy_of"]
            ef = float(EF_REAL[proxy_sector])
            table.append({
                "region": region,
                "sector": sector,
                "price_year": price_year,
                "currency": currency,
                "ef_kg_per_currency": ef,
                "note": f"proxy_of:{proxy_sector}; reason:{proxy['reason']}",
            })
    return table


def estimate_emissions_exiobase_single(*, country: str, sector: str, revenue: float, currency: str, rev_price_year: int, ef_table: List[Dict[str, Union[str, float, int]]], ef_price_year: Optional[int] = None, ef_currency: Optional[str] = None, fx_to_ef_currency: float = 1.0, deflator_to_ef_year: float = 1.0) -> Dict[str, Union[str, float, Dict[str, float]]]:
    gcc = {"United Arab Emirates", "Saudi Arabia", "Oman", "Qatar", "Bahrain", "Kuwait"}
    if country not in gcc:
        raise ValueError(f"Country must be one of: {', '.join(sorted(gcc))}")

    sector_in = canonicalize_sector(sector)
    if sector_in not in SUPPORTED_SECTORS_GCC:
        raise ValueError(f"Unsupported sector '{sector}'.")

    def _norm(x: str) -> str:
        return str(x).strip().lower()

    candidates = [row for row in ef_table if _norm(str(row["sector"])) == _norm(sector_in)]
    if ef_price_year is not None:
        candidates = [row for row in candidates if int(row["price_year"]) == int(ef_price_year)]
    if ef_currency is not None:
        candidates = [row for row in candidates if _norm(str(row["currency"])) == _norm(ef_currency)]
    if not candidates:
        raise KeyError(f"No EF row matched for sector={sector_in}")

    ef_row = candidates[0]
    ef_val = float(ef_row["ef_kg_per_currency"])
    revenue_in_ef_units = float(revenue) * float(fx_to_ef_currency) * float(deflator_to_ef_year)
    total_kg = revenue_in_ef_units * ef_val
    total_t = total_kg / 1000.0

    shares = SECTOR_SCOPE_SHARES_GCC.get(sector_in, {"scope1": 0.1, "scope2": 0.1, "scope3": 0.8})
    denom = shares["scope1"] + shares["scope2"] + shares["scope3"] or 1.0
    s1 = shares["scope1"] / denom
    s2 = shares["scope2"] / denom
    s3 = shares["scope3"] / denom

    return {
        "country": country,
        "sector": sector_in,
        "ef_currency": str(ef_row["currency"]),
        "ef_price_year": int(ef_row["price_year"]),
        "ef_note": str(ef_row.get("note", "")),
        "revenue_input": revenue,
        "revenue_currency": currency,
        "rev_price_year": rev_price_year,
        "revenue_in_ef_units": revenue_in_ef_units,
        "ef_kg_per_currency": ef_val,
        "total_tCO2e": total_t,
        "scope1_tCO2e": total_t * s1,
        "scope2_tCO2e": total_t * s2,
        "scope3_tCO2e": total_t * s3,
        "scope_shares_used": {"scope1": s1, "scope2": s2, "scope3": s3},
    }
