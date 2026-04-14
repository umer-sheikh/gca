from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from gulf_climate_agent.controller.tool_controller import RouteDecision


@dataclass(slots=True)
class AgentStep:
    index: int
    kind: str
    payload: dict[str, Any]


@dataclass(slots=True)
class AgentRunResult:
    query: str
    final_answer: str
    route: RouteDecision
    steps: list[AgentStep] = field(default_factory=list)
    raw_messages: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "query": self.query,
            "final_answer": self.final_answer,
            "route": {
                "dominant_intent": self.route.dominant_intent,
                "enabled_tools": self.route.enabled_tools,
                "domain_scores": self.route.domain_scores,
                "rationale": self.route.rationale,
            },
            "steps": [
                {"index": step.index, "kind": step.kind, "payload": step.payload}
                for step in self.steps
            ],
            "raw_messages": self.raw_messages,
        }
