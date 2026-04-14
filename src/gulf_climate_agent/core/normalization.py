from __future__ import annotations

import math
import statistics
from datetime import datetime, timezone
from typing import Any


def utc_now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


def summarize_numeric(values: list[float | int | None]) -> dict[str, Any]:
    clean = [float(v) for v in values if v is not None and not math.isnan(float(v))]
    if not clean:
        return {"count": 0, "min": None, "max": None, "mean": None, "median": None, "std": None}
    return {
        "count": len(clean),
        "min": float(min(clean)),
        "max": float(max(clean)),
        "mean": float(statistics.fmean(clean)),
        "median": float(statistics.median(clean)),
        "std": float(statistics.pstdev(clean)) if len(clean) > 1 else 0.0,
    }


def infer_trend(values: list[float | int | None]) -> dict[str, Any]:
    clean = [float(v) for v in values if v is not None]
    if len(clean) < 2:
        return {"direction": "unknown", "delta": None}
    delta = clean[-1] - clean[0]
    eps = max(abs(sum(clean) / len(clean)) * 0.02, 1e-9)
    if delta > eps:
        direction = "increasing"
    elif delta < -eps:
        direction = "decreasing"
    else:
        direction = "stable"
    return {"direction": direction, "delta": float(delta)}


def to_time_series(timestamps: list[str], values: dict[str, list[float | None]], units: dict[str, str] | None = None) -> dict[str, Any]:
    return {
        "timestamps": timestamps,
        "values": values,
        "units": units or {},
    }
