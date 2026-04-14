from __future__ import annotations

from pydantic import BaseModel, Field


class BenchmarkCase(BaseModel):
    case_id: str
    query: str
    expected_tools: list[str] = Field(default_factory=list)
    execute_agent: bool = False
    notes: str | None = None


class BenchmarkCaseResult(BaseModel):
    case_id: str
    query: str
    routed_tools: list[str]
    expected_tools: list[str]
    route_hit: bool
    used_tools: list[str] = Field(default_factory=list)
    execution_hit: bool | None = None
    final_answer: str | None = None
