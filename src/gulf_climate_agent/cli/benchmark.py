from __future__ import annotations

import argparse
import json

from gulf_climate_agent.agent.factory import build_default_agent
from gulf_climate_agent.benchmarks.runner import BenchmarkRunner
from gulf_climate_agent.config.settings import Settings


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the lightweight GCA benchmark harness.")
    parser.add_argument("--cases", required=True, help="Path to benchmark case JSONL file")
    parser.add_argument("--json", action="store_true", help="Emit JSON only")
    args = parser.parse_args()

    settings = Settings.load()
    agent = build_default_agent(settings)
    runner = BenchmarkRunner(agent)
    cases = runner.load_cases(args.cases)
    results = runner.run_cases(cases)
    summary = runner.summarize(results)
    payload = {
        "summary": summary,
        "results": [row.model_dump(mode="json") for row in results],
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
