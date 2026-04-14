from __future__ import annotations

import argparse
import json

from gulf_climate_agent.agent.factory import build_default_agent
from gulf_climate_agent.config.settings import Settings
from gulf_climate_agent.tools.registry import build_tool_registry


def _print_json(payload: dict) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Gulf Climate Agent or invoke a single tool.")
    parser.add_argument("--query", type=str, help="Natural-language query for the agent")
    parser.add_argument("--tool", type=str, help="Invoke a specific tool by name")
    parser.add_argument("--payload", type=str, default="{}", help="JSON payload for direct tool invocation")
    parser.add_argument("--list-tools", action="store_true", help="List registered tool names")
    parser.add_argument("--trace", action="store_true", help="Include route and step trace in output")
    args = parser.parse_args()

    settings = Settings.load()
    registry = build_tool_registry(settings)

    if args.list_tools:
        _print_json({"tools": registry.names()})
        return

    if args.tool:
        payload = json.loads(args.payload)
        tool = registry.tool_map[args.tool]
        result = tool.invoke(payload)
        _print_json(result)
        return

    if not args.query:
        parser.error("either --query or --tool must be provided")

    agent = build_default_agent(settings)
    result = agent.invoke(args.query)
    if args.trace:
        _print_json(result.to_dict())
        return
    _print_json({"answer": result.final_answer, "route": result.route.enabled_tools})


if __name__ == "__main__":
    main()
