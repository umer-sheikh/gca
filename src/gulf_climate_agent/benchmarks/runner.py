from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from gulf_climate_agent.agent.runtime import LangChainGCAAgent
from gulf_climate_agent.benchmarks.schemas import BenchmarkCase, BenchmarkCaseResult


class BenchmarkRunner:
    def __init__(self, agent: LangChainGCAAgent) -> None:
        self.agent = agent

    def load_cases(self, path: str | Path) -> list[BenchmarkCase]:
        rows: list[BenchmarkCase] = []
        for line in Path(path).read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            rows.append(BenchmarkCase.model_validate(json.loads(line)))
        return rows

    def run_case(self, case: BenchmarkCase) -> BenchmarkCaseResult:
        route = self.agent.controller.decide(case.query)
        routed_tools = route.enabled_tools
        route_hit = all(tool in routed_tools for tool in case.expected_tools)
        used_tools: list[str] = []
        execution_hit: bool | None = None
        final_answer: str | None = None
        if case.execute_agent:
            result = self.agent.invoke(case.query)
            used_tools = [step.payload.get("tool") for step in result.steps if step.kind == "tool_call"]
            final_answer = result.final_answer
            execution_hit = all(tool in used_tools for tool in case.expected_tools)
        return BenchmarkCaseResult(
            case_id=case.case_id,
            query=case.query,
            routed_tools=routed_tools,
            expected_tools=case.expected_tools,
            route_hit=route_hit,
            used_tools=[tool for tool in used_tools if tool],
            execution_hit=execution_hit,
            final_answer=final_answer,
        )

    def run_cases(self, cases: Iterable[BenchmarkCase]) -> list[BenchmarkCaseResult]:
        return [self.run_case(case) for case in cases]

    def summarize(self, results: list[BenchmarkCaseResult]) -> dict:
        if not results:
            return {"n_cases": 0, "route_hit_rate": None, "execution_hit_rate": None}
        route_hits = sum(1 for row in results if row.route_hit)
        executable = [row for row in results if row.execution_hit is not None]
        exec_hits = sum(1 for row in executable if row.execution_hit)
        return {
            "n_cases": len(results),
            "route_hit_rate": route_hits / len(results),
            "execution_hit_rate": (exec_hits / len(executable)) if executable else None,
        }
