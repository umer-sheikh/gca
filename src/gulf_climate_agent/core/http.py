from __future__ import annotations

import time
from typing import Any

import requests

from gulf_climate_agent.core.exceptions import ProviderAPIError


class JsonHttpClient:
    def __init__(self, *, timeout: int = 60, retries: int = 3, user_agent: str = "GulfClimateAgent/0.1") -> None:
        self.timeout = timeout
        self.retries = retries
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": user_agent})

    def _request(self, method: str, url: str, **kwargs: Any) -> requests.Response:
        last_error: Exception | None = None
        for attempt in range(1, self.retries + 1):
            try:
                response = self.session.request(method, url, timeout=self.timeout, **kwargs)
                if response.status_code >= 500:
                    raise ProviderAPIError(f"server-side error from {url}: {response.status_code}")
                response.raise_for_status()
                return response
            except Exception as exc:
                last_error = exc
                if attempt >= self.retries:
                    break
                time.sleep(min(1.75 ** attempt, 8.0))
        raise ProviderAPIError(f"HTTP request failed for {url}: {last_error}")

    def get_json(self, url: str, *, params: dict[str, Any] | None = None, headers: dict[str, str] | None = None) -> dict[str, Any]:
        response = self._request("GET", url, params=params, headers=headers)
        data = response.json()
        if isinstance(data, dict) and data.get("error") is True:
            raise ProviderAPIError(str(data.get("reason") or data))
        return data

    def post_json(self, url: str, *, body: dict[str, Any], headers: dict[str, str] | None = None) -> dict[str, Any]:
        response = self._request("POST", url, json=body, headers=headers)
        data = response.json()
        if isinstance(data, dict) and data.get("error") is True:
            raise ProviderAPIError(str(data.get("reason") or data))
        return data

    def get_bytes(self, url: str, *, headers: dict[str, str] | None = None) -> bytes:
        response = self._request("GET", url, headers=headers)
        return response.content
