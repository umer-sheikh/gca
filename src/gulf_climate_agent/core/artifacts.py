from __future__ import annotations

import hashlib
import io
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

import numpy as np

from gulf_climate_agent.contracts.base import ArtifactRef
from gulf_climate_agent.core.exceptions import ArtifactNotFoundError


class ArtifactStore:
    def __init__(self, root: Path) -> None:
        self.root = root.expanduser().resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def _timestamp(self) -> str:
        return datetime.now(tz=timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    def _sha256(self, data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    def _allocate(self, namespace: str, suffix: str) -> Path:
        directory = self.root / namespace
        directory.mkdir(parents=True, exist_ok=True)
        return directory / f"{self._timestamp()}_{uuid4().hex}{suffix}"

    def _to_uri(self, path: Path) -> str:
        return f"artifact://{path.relative_to(self.root).as_posix()}"

    def _meta_path(self, path: Path) -> Path:
        return path.with_suffix(path.suffix + ".meta.json")

    def write_bytes(self, *, namespace: str, suffix: str, data: bytes, media_type: str, kind: str, metadata: dict[str, Any] | None = None) -> ArtifactRef:
        path = self._allocate(namespace, suffix)
        path.write_bytes(data)
        ref = ArtifactRef(
            uri=self._to_uri(path),
            media_type=media_type,
            kind=kind,
            size_bytes=len(data),
            sha256=self._sha256(data),
            metadata=metadata or {},
        )
        self._meta_path(path).write_text(ref.model_dump_json(indent=2), encoding="utf-8")
        return ref

    def write_json(self, *, namespace: str, payload: dict[str, Any], kind: str = "json") -> ArtifactRef:
        data = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        return self.write_bytes(namespace=namespace, suffix=".json", data=data, media_type="application/json", kind=kind, metadata={})

    def write_text(self, *, namespace: str, text: str, kind: str = "text") -> ArtifactRef:
        data = text.encode("utf-8")
        return self.write_bytes(namespace=namespace, suffix=".txt", data=data, media_type="text/plain", kind=kind, metadata={})

    def write_npz(self, *, namespace: str, arrays: dict[str, Any], metadata: dict[str, Any] | None = None, kind: str = "ndarray") -> ArtifactRef:
        buffer = io.BytesIO()
        np.savez_compressed(buffer, **arrays)
        return self.write_bytes(
            namespace=namespace,
            suffix=".npz",
            data=buffer.getvalue(),
            media_type="application/octet-stream",
            kind=kind,
            metadata=metadata or {},
        )

    def resolve(self, ref_or_uri: ArtifactRef | str) -> Path:
        uri = ref_or_uri.uri if isinstance(ref_or_uri, ArtifactRef) else ref_or_uri
        if uri.startswith("artifact://"):
            relative = uri.removeprefix("artifact://")
            path = self.root / relative
        else:
            path = Path(uri).expanduser().resolve()
        if not path.exists():
            raise ArtifactNotFoundError(f"artifact not found: {uri}")
        return path

    def read_meta(self, ref_or_uri: ArtifactRef | str) -> dict[str, Any]:
        path = self.resolve(ref_or_uri)
        meta_path = self._meta_path(path)
        if not meta_path.exists():
            return {}
        return json.loads(meta_path.read_text(encoding="utf-8"))

    def read_json(self, ref_or_uri: ArtifactRef | str) -> dict[str, Any]:
        path = self.resolve(ref_or_uri)
        return json.loads(path.read_text(encoding="utf-8"))

    def read_text(self, ref_or_uri: ArtifactRef | str) -> str:
        path = self.resolve(ref_or_uri)
        return path.read_text(encoding="utf-8")

    def read_npz(self, ref_or_uri: ArtifactRef | str) -> dict[str, Any]:
        path = self.resolve(ref_or_uri)
        with np.load(path, allow_pickle=True) as payload:
            return {key: payload[key] for key in payload.files}
