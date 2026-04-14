from __future__ import annotations

import json
from typing import Any

from gulf_climate_agent.core.langchain_compat import ChatOpenAI, HumanMessage, SystemMessage, ToolMessage

from gulf_climate_agent.agent.prompts import build_system_prompt
from gulf_climate_agent.agent.state import AgentRunResult, AgentStep
from gulf_climate_agent.config.settings import Settings
from gulf_climate_agent.controller.tool_controller import ToolController
from gulf_climate_agent.core.serialization import to_jsonable
from gulf_climate_agent.core.tracing import trace_session
from gulf_climate_agent.tools.registry import ToolRegistry


class LangChainGCAAgent:
    def __init__(
        self,
        *,
        settings: Settings,
        registry: ToolRegistry,
        controller: ToolController | None = None,
        llm: ChatOpenAI | None = None,
    ) -> None:
        self.settings = settings
        self.registry = registry
        self.controller = controller or ToolController()
        self.llm = llm

    def _build_llm(self) -> ChatOpenAI:
        kwargs: dict[str, Any] = {
            "model": self.settings.openai.model,
            "api_key": self.settings.openai.api_key,
        }
        if self.settings.openai.base_url:
            kwargs["base_url"] = self.settings.openai.base_url
        return ChatOpenAI(**kwargs)

    def _normalize_content(self, content: Any) -> str:
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            chunks: list[str] = []
            for item in content:
                if isinstance(item, str):
                    chunks.append(item)
                elif isinstance(item, dict):
                    text = item.get("text") or item.get("content") or json.dumps(item, ensure_ascii=False)
                    chunks.append(str(text))
                else:
                    chunks.append(str(item))
            return "\n".join(chunks).strip()
        return str(content)

    def invoke(self, query: str) -> AgentRunResult:
        route = self.controller.decide(query)
        active_tools = self.registry.select(route.enabled_tools)
        llm = self.llm or self._build_llm()
        self.llm = llm
        bound_model = llm.bind_tools(active_tools) if active_tools else llm
        system_prompt = build_system_prompt(route, [tool.name for tool in active_tools])
        messages: list[Any] = [SystemMessage(content=system_prompt), HumanMessage(content=query)]
        steps: list[AgentStep] = []
        raw_messages: list[dict[str, Any]] = []

        with trace_session() as trace:
            trace.log("route_decision", {"route": to_jsonable(route.__dict__)})
            for iteration in range(1, self.settings.agent.max_iterations + 1):
                ai_message = bound_model.invoke(messages)
                raw_messages.append({"iteration": iteration, "ai_message": to_jsonable(ai_message.model_dump())})
                messages.append(ai_message)

                tool_calls = getattr(ai_message, "tool_calls", None) or []
                if not tool_calls:
                    final_answer = self._normalize_content(ai_message.content)
                    steps.append(AgentStep(index=iteration, kind="final", payload={"answer": final_answer}))
                    trace.log("final_answer", {"answer": final_answer})
                    return AgentRunResult(
                        query=query,
                        final_answer=final_answer,
                        route=route,
                        steps=steps,
                        raw_messages=raw_messages,
                    )

                for tool_call in tool_calls:
                    tool_name = tool_call["name"]
                    tool_args = tool_call.get("args") or {}
                    tool = self.registry.tool_map[tool_name]
                    observation = tool.invoke(tool_args)
                    observation_payload = to_jsonable(observation)
                    steps.append(
                        AgentStep(
                            index=iteration,
                            kind="tool_call",
                            payload={"tool": tool_name, "args": tool_args, "observation": observation_payload},
                        )
                    )
                    trace.log(
                        "tool_call",
                        {"tool": tool_name, "args": tool_args, "observation": observation_payload},
                    )
                    messages.append(
                        ToolMessage(
                            content=json.dumps(observation_payload, ensure_ascii=False),
                            tool_call_id=tool_call["id"],
                            name=tool_name,
                        )
                    )

            fallback_answer = (
                "Maximum agent iterations reached before a final answer was produced. "
                "Inspect the trace for intermediate tool outputs."
            )
            trace.log("max_iterations", {"answer": fallback_answer})
            return AgentRunResult(
                query=query,
                final_answer=fallback_answer,
                route=route,
                steps=steps,
                raw_messages=raw_messages,
            )
