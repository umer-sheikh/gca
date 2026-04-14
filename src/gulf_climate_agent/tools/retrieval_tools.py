from __future__ import annotations

from gulf_climate_agent.contracts.retrieval import OnlineSearchInput, OnlineSearchOutput, SearchResult, SummarizeInput, SummarizeOutput
from gulf_climate_agent.tools.base import ToolServices, build_meta, dump_model, make_structured_tool


RETRIEVAL_DESCRIPTIONS = {
    "online_search": "Search the web for policies, reports, or climate events using Tavily and return ranked results with snippets.",
    "summarize": "Summarize a supplied text with GPT-5 while preserving key factual details.",
}


def build_retrieval_tools(services: ToolServices):
    tavily = services.tavily
    openai_client = services.openai

    def online_search(query: str):
        payload = OnlineSearchInput(query=query)
        results = tavily.search(payload.query)
        output = OnlineSearchOutput(
            meta=build_meta(provider="tavily", source=services.settings.tavily.search_url),
            results=[SearchResult(**row) for row in results],
        )
        return dump_model(output)

    def summarize(text: str):
        payload = SummarizeInput(text=text)
        summary = openai_client.summarize(payload.text)
        output = SummarizeOutput(
            meta=build_meta(provider="gpt-5", source="openai.responses"),
            summary=summary,
        )
        return dump_model(output)

    return [
        make_structured_tool(name="online_search", description=RETRIEVAL_DESCRIPTIONS["online_search"], args_schema=OnlineSearchInput, fn=online_search),
        make_structured_tool(name="summarize", description=RETRIEVAL_DESCRIPTIONS["summarize"], args_schema=SummarizeInput, fn=summarize),
    ]
