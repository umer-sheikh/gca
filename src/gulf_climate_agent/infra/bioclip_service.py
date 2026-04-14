from __future__ import annotations

import json
import subprocess

from gulf_climate_agent.config.settings import Settings
from gulf_climate_agent.core.exceptions import ProviderAPIError


class BioClipClassifier:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def classify(self, image_path: str, *, top_k: int | None = None) -> list[dict]:
        command = [
            self.settings.bioclip_bin,
            "predict",
            image_path,
            "--output",
            "json",
            "--top-k",
            str(int(top_k or self.settings.bioclip_top_k)),
        ]
        try:
            result = subprocess.run(command, check=True, capture_output=True, text=True)
        except FileNotFoundError as exc:
            raise ProviderAPIError("BioCLIP CLI not found in PATH.") from exc
        except subprocess.CalledProcessError as exc:
            raise ProviderAPIError(exc.stderr or exc.stdout) from exc

        payload = json.loads(result.stdout)
        rows = payload if isinstance(payload, list) else payload.get("predictions", [])
        normalized: list[dict] = []
        for item in rows:
            if not isinstance(item, dict):
                continue
            normalized.append(
                {
                    "species": item.get("label") or item.get("species") or item.get("name") or "unknown",
                    "confidence": float(item.get("score") or item.get("confidence") or item.get("prob") or 0.0),
                }
            )
        return normalized
