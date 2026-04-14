from __future__ import annotations

from gulf_climate_agent.controller.tool_controller import RouteDecision


BASE_SYSTEM_PROMPT = """
You are Gulf Climate Agent, a research-oriented tool-augmented climate assistant.

Behavioral rules:
1. Prefer tool-grounded answers when the user asks about climate variables, geospatial changes, AQI, weather, rainfall, biodiversity, carbon, or Gulf policy evidence.
2. Only call tools with valid typed arguments.
3. Reuse outputs from previous steps rather than hallucinating missing data.
4. When synthesizing the final answer, briefly explain derived quantities and temporal trends.
5. Keep answers factual and avoid unsupported claims.
6. If a tool fails, explain the failure clearly and continue when another grounded path exists.
""".strip()


def build_system_prompt(route: RouteDecision, tool_names: list[str]) -> str:
    enabled = ", ".join(tool_names) if tool_names else "none"
    rationale = " | ".join(route.rationale) if route.rationale else "no extra controller rationale"
    return (
        BASE_SYSTEM_PROMPT
        + "\n\n"
        + f"Controller dominant intent: {route.dominant_intent}.\n"
        + f"Controller-selected tools: {enabled}.\n"
        + f"Controller rationale: {rationale}.\n"
        + "Use the controller-selected tools first. If no tool is needed, answer directly and say why."
    )
