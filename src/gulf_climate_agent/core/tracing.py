from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Iterator
from uuid import uuid4


def _utc_now() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


@dataclass(slots=True)
class TraceEvent:
    ts: str
    kind: str
    payload: dict[str, Any]


@dataclass(slots=True)
class TraceCollector:
    correlation_id: str = field(default_factory=lambda: uuid4().hex)
    events: list[TraceEvent] = field(default_factory=list)

    def log(self, kind: str, payload: dict[str, Any]) -> None:
        self.events.append(TraceEvent(ts=_utc_now(), kind=kind, payload=payload))


_CURRENT_TRACE: ContextVar[TraceCollector | None] = ContextVar("gca_trace", default=None)


@contextmanager
def trace_session(correlation_id: str | None = None) -> Iterator[TraceCollector]:
    collector = TraceCollector(correlation_id=correlation_id or uuid4().hex)
    token = _CURRENT_TRACE.set(collector)
    try:
        yield collector
    finally:
        _CURRENT_TRACE.reset(token)


def get_trace() -> TraceCollector | None:
    return _CURRENT_TRACE.get()
