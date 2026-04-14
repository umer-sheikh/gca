from __future__ import annotations

import json
from functools import cached_property
from typing import Any

from gulf_climate_agent.config.settings import Settings
from gulf_climate_agent.core.exceptions import ConfigurationError, ProviderAPIError


class OpenAIResponsesClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    @cached_property
    def client(self):
        if not self.settings.openai.api_key:
            raise ConfigurationError("OPENAI_API_KEY is required for GPT-5 backed tools.")
        from openai import OpenAI

        kwargs: dict[str, Any] = {"api_key": self.settings.openai.api_key}
        if self.settings.openai.base_url:
            kwargs["base_url"] = self.settings.openai.base_url
        return OpenAI(**kwargs)

    def _create_text(self, *, instructions: str, input_text: str) -> str:
        payload: dict[str, Any] = {
            "model": self.settings.openai.model,
            "instructions": instructions,
            "input": input_text,
        }
        if self.settings.openai.reasoning_effort:
            payload["reasoning"] = {"effort": self.settings.openai.reasoning_effort}
        response = self.client.responses.create(**payload)
        text = getattr(response, "output_text", None)
        if text:
            return str(text).strip()

        output = getattr(response, "output", None)
        if not output:
            raise ProviderAPIError("OpenAI Responses API returned no textual output.")

        chunks: list[str] = []
        for item in output:
            for content in getattr(item, "content", []) or []:
                if getattr(content, "type", None) == "output_text":
                    chunks.append(getattr(content, "text", ""))
        if not chunks:
            raise ProviderAPIError("OpenAI Responses API returned an unsupported payload shape.")
        return "\n".join(chunks).strip()

    def summarize(self, text: str) -> str:
        instructions = (
            "You are Gulf Climate Agent. Produce a concise factual summary. "
            "Preserve numbers, dates, causal qualifiers, and policy implications. "
            "Do not invent facts not contained in the supplied text."
        )
        return self._create_text(instructions=instructions, input_text=text)

    def desertification_analysis(self, context: dict[str, Any]) -> str:
        instructions = (
            "You are a climate remote-sensing analyst. "
            "Given structured change metrics from two satellite observations, explain whether the area shows "
            "evidence of desertification progression, recovery, or ambiguous change. "
            "Ground the explanation in NDVI and NDWI deltas and affected-area fractions. "
            "Keep the tone analytical and concise."
        )
        return self._create_text(
            instructions=instructions,
            input_text=json.dumps(context, indent=2, ensure_ascii=False),
        )
