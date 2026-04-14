from __future__ import annotations

from gulf_climate_agent.config.settings import Settings
from gulf_climate_agent.core.exceptions import ConfigurationError
from gulf_climate_agent.core.http import JsonHttpClient


class TavilySearchClient:
    def __init__(self, settings: Settings, http: JsonHttpClient) -> None:
        self.settings = settings
        self.http = http

    def search(self, query: str, *, max_results: int | None = None) -> list[dict]:
        if not self.settings.tavily.api_key:
            raise ConfigurationError("TAVILY_API_KEY is required for online_search.")

        body = {
            "query": query,
            "topic": "general",
            "search_depth": "advanced",
            "max_results": max_results or self.settings.tavily.max_results,
            "include_answer": False,
            "include_raw_content": False,
        }
        headers = {
            "Authorization": f"Bearer {self.settings.tavily.api_key}",
            "Content-Type": "application/json",
        }
        data = self.http.post_json(self.settings.tavily.search_url, body=body, headers=headers)
        results: list[dict] = []
        for item in data.get("results", []) or []:
            results.append(
                {
                    "title": item.get("title") or "",
                    "url": item.get("url") or "",
                    "snippet": item.get("content") or item.get("snippet") or "",
                }
            )
        return results
