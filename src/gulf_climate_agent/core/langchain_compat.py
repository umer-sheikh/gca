from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from gulf_climate_agent.core.exceptions import MissingDependencyError


try:
    from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage  # type: ignore
    from langchain_core.tools import BaseTool, StructuredTool  # type: ignore
    from langchain_openai import ChatOpenAI  # type: ignore
except Exception:
    @dataclass
    class _CompatMessage:
        content: Any

        def model_dump(self) -> dict[str, Any]:
            return {"content": self.content}


    @dataclass
    class AIMessage(_CompatMessage):
        tool_calls: list[dict[str, Any]] = field(default_factory=list)


    @dataclass
    class HumanMessage(_CompatMessage):
        pass


    @dataclass
    class SystemMessage(_CompatMessage):
        pass


    @dataclass
    class ToolMessage(_CompatMessage):
        tool_call_id: str = ""
        name: str = ""


    class BaseTool:
        name: str
        description: str
        args_schema: type | None

        def invoke(self, input: dict[str, Any]) -> Any:
            raise NotImplementedError


    class StructuredTool(BaseTool):
        def __init__(self, *, name: str, description: str, args_schema: type | None, func: Callable[..., Any], return_direct: bool = False) -> None:
            self.name = name
            self.description = description
            self.args_schema = args_schema
            self.func = func
            self.return_direct = return_direct

        @classmethod
        def from_function(cls, *, name: str, description: str, args_schema: type | None, func: Callable[..., Any], return_direct: bool = False):
            return cls(name=name, description=description, args_schema=args_schema, func=func, return_direct=return_direct)

        def invoke(self, input: dict[str, Any]) -> Any:
            if input is None:
                input = {}
            return self.func(**input)


    class ChatOpenAI:
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            raise MissingDependencyError(
                "LangChain and langchain-openai are required for agent execution. Install project dependencies first."
            )
