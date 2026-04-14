from __future__ import annotations

from pydantic import BaseModel

from gulf_climate_agent.contracts.base import ClimateToolOutput


class OnlineSearchInput(BaseModel):
    query: str


class SearchResult(BaseModel):
    title: str
    url: str
    snippet: str


class OnlineSearchOutput(ClimateToolOutput):
    results: list[SearchResult]


class SummarizeInput(BaseModel):
    text: str


class SummarizeOutput(ClimateToolOutput):
    summary: str
