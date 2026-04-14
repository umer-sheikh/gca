from __future__ import annotations

import json
from functools import cached_property
from pathlib import Path

from gulf_climate_agent.config.settings import Settings
from gulf_climate_agent.core.exceptions import ConfigurationError, MissingDependencyError


class BirdCallClassifier:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    @cached_property
    def model_path(self) -> Path:
        if not self.settings.birds.model_path:
            raise ConfigurationError("BIRD_MODEL_PATH is required for detect_bird.")
        return self.settings.birds.model_path

    @cached_property
    def labels_path(self) -> Path:
        if not self.settings.birds.labels_path:
            raise ConfigurationError("BIRD_LABELS_PATH is required for detect_bird.")
        return self.settings.birds.labels_path

    @cached_property
    def labels(self) -> list[str]:
        payload = json.loads(self.labels_path.read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            try:
                return [payload[str(i)] for i in range(len(payload))]
            except Exception:
                return list(payload.values())
        return list(payload)

    @cached_property
    def model(self):
        try:
            import tensorflow as tf
        except Exception as exc:
            raise MissingDependencyError("tensorflow is required for detect_bird") from exc
        return tf.keras.models.load_model(str(self.model_path), compile=False)

    def _extract_features(self, audio_clip: str):
        try:
            import librosa
            import numpy as np
        except Exception as exc:
            raise MissingDependencyError("librosa and numpy are required for detect_bird") from exc

        y, sr = librosa.load(
            audio_clip,
            sr=self.settings.birds.sample_rate,
            duration=float(self.settings.birds.clip_seconds),
        )
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=self.settings.birds.n_mfcc)
        return np.mean(mfcc.T, axis=0).reshape(1, self.settings.birds.n_mfcc)

    def classify(self, audio_clip: str, *, top_n: int | None = None) -> list[dict]:
        import numpy as np

        features = self._extract_features(audio_clip)
        preds = self.model.predict(features, verbose=0)[0]
        n = max(1, int(top_n or self.settings.birds.top_n))
        indices = np.argsort(preds)[::-1][:n]
        results: list[dict] = []
        for idx in indices:
            label = self.labels[int(idx)] if int(idx) < len(self.labels) else f"class_{int(idx)}"
            results.append({"species": label, "confidence": float(preds[int(idx)])})
        return results
