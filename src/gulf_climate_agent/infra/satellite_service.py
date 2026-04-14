from __future__ import annotations

import io
import json
from datetime import datetime, timedelta
from typing import Any

import numpy as np

from gulf_climate_agent.config.settings import Settings
from gulf_climate_agent.core.artifacts import ArtifactStore
from gulf_climate_agent.core.exceptions import ProviderAPIError, ToolExecutionError
from gulf_climate_agent.core.http import JsonHttpClient
from gulf_climate_agent.core.normalization import summarize_numeric
from gulf_climate_agent.infra.earth_engine_session import EarthEngineSession


class Sentinel2Service:
    def __init__(self, settings: Settings, artifacts: ArtifactStore, http: JsonHttpClient, ee_session: EarthEngineSession) -> None:
        self.settings = settings
        self.artifacts = artifacts
        self.http = http
        self.ee_session = ee_session

    def _build_aoi(self, ee, lat: float, lon: float):
        point = ee.Geometry.Point([lon, lat])
        return point.buffer(self.settings.satellite.buffer_meters).bounds()

    def _load_collection(self, ee, aoi, date: str):
        target = datetime.strptime(date, "%Y-%m-%d")
        start = (target - timedelta(days=self.settings.satellite.search_window_days)).strftime("%Y-%m-%d")
        end = (target + timedelta(days=self.settings.satellite.search_window_days + 1)).strftime("%Y-%m-%d")
        collection = (
            ee.ImageCollection(self.settings.satellite.collection)
            .filterBounds(aoi)
            .filterDate(start, end)
            .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", self.settings.satellite.max_cloud_pct))
        )
        return collection, start, end

    def _sample_array(self, image, aoi, band_name: str) -> np.ndarray:
        payload = image.clip(aoi).sampleRectangle(region=aoi, defaultValue=-9999).getInfo()
        props = payload.get("properties", {})
        raw = props.get(band_name)
        if raw is None:
            raise ProviderAPIError(f"band {band_name} not present in sampleRectangle payload")
        arr = np.asarray(raw, dtype=np.float32)
        arr[arr <= -9998] = np.nan
        return arr

    def _plot_array(self, array: np.ndarray, *, cmap: str, label: str, namespace: str) -> Any:
        import matplotlib.pyplot as plt

        fig = plt.figure(figsize=(6, 6), dpi=180)
        ax = fig.add_subplot(111)
        masked = np.ma.masked_invalid(array)
        im = ax.imshow(masked, cmap=cmap, vmin=-1.0, vmax=1.0)
        ax.set_title(label)
        ax.set_axis_off()
        fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        buffer = io.BytesIO()
        fig.savefig(buffer, format="png", bbox_inches="tight")
        plt.close(fig)
        return self.artifacts.write_bytes(
            namespace=namespace,
            suffix=".png",
            data=buffer.getvalue(),
            media_type="image/png",
            kind="map",
            metadata={"label": label},
        )

    def _index_stats(self, array: np.ndarray, *, threshold: float) -> dict[str, Any]:
        flat = array[~np.isnan(array)].ravel().tolist()
        summary = summarize_numeric(flat)
        total = int(array.size) if array.size else 1
        valid = int(np.isfinite(array).sum())
        positive = int((array > 0).sum()) if valid else 0
        negative = int((array < 0).sum()) if valid else 0
        threshold_hits = int((array > threshold).sum()) if valid else 0
        summary.update(
            {
                "valid_fraction": float(valid / total),
                "positive_fraction": float(positive / valid) if valid else 0.0,
                "negative_fraction": float(negative / valid) if valid else 0.0,
                "threshold_fraction": float(threshold_hits / valid) if valid else 0.0,
            }
        )
        return summary

    def get_satellite_image(self, *, lat: float, lon: float, date: str) -> dict[str, Any]:
        ee = self.ee_session.get_ee()
        aoi = self._build_aoi(ee, lat, lon)
        collection, start, end = self._load_collection(ee, aoi, date)
        count = int(collection.size().getInfo())
        if count <= 0:
            raise ToolExecutionError(f"No Sentinel-2 scenes found near ({lat}, {lon}) around {date}")

        image = ee.Image(collection.sort("CLOUDY_PIXEL_PERCENTAGE").median())
        rgb_visual = image.divide(10000).visualize(bands=["B4", "B3", "B2"], min=0.02, max=0.35)
        rgb_url = rgb_visual.getThumbURL({"region": aoi, "dimensions": self.settings.satellite.thumb_size, "format": "png"})
        rgb_bytes = self.http.get_bytes(rgb_url)

        ndvi = image.normalizedDifference(["B8", "B4"]).rename("ndvi")
        ndwi = image.normalizedDifference(["B3", "B8"]).rename("ndwi")

        ndvi_array = self._sample_array(ndvi, aoi, "ndvi")
        ndwi_array = self._sample_array(ndwi, aoi, "ndwi")

        rgb_ref = self.artifacts.write_bytes(
            namespace="remote_sensing/rgb",
            suffix=".png",
            data=rgb_bytes,
            media_type="image/png",
            kind="rgb_preview",
            metadata={"lat": lat, "lon": lon, "date": date},
        )
        ndvi_ref = self.artifacts.write_npz(
            namespace="remote_sensing/index",
            arrays={"array": ndvi_array},
            metadata={"lat": lat, "lon": lon, "date": date, "index": "ndvi", "formula": "(B8-B4)/(B8+B4)"},
            kind="ndvi_index",
        )
        ndwi_ref = self.artifacts.write_npz(
            namespace="remote_sensing/index",
            arrays={"array": ndwi_array},
            metadata={"lat": lat, "lon": lon, "date": date, "index": "ndwi", "formula": "(B3-B8)/(B3+B8)"},
            kind="ndwi_index",
        )

        manifest = {
            "lat": lat,
            "lon": lon,
            "date": date,
            "window_start": start,
            "window_end": end,
            "scene_count": count,
            "collection": self.settings.satellite.collection,
            "rgb_img": rgb_ref.model_dump(mode="json"),
            "ndvi_index": ndvi_ref.model_dump(mode="json"),
            "ndwi_index": ndwi_ref.model_dump(mode="json"),
        }
        image_ref = self.artifacts.write_json(namespace="remote_sensing/manifest", payload=manifest, kind="satellite_manifest")
        return {
            "rgb_img": rgb_ref,
            "ndvi_index": ndvi_ref,
            "ndwi_index": ndwi_ref,
            "image_ref": image_ref,
            "metadata": {k: v for k, v in manifest.items() if k not in {"rgb_img", "ndvi_index", "ndwi_index"}},
        }

    def _resolve_ref(self, value: str | dict[str, Any]) -> str:
        if isinstance(value, dict):
            if "uri" in value:
                return str(value["uri"])
            raise ToolExecutionError("expected artifact dict with 'uri'")
        return value

    def _resolve_manifest(self, image: str) -> dict[str, Any]:
        if image.startswith("artifact://"):
            meta = self.artifacts.read_meta(image)
            if meta.get("kind") == "satellite_manifest":
                return self.artifacts.read_json(image)
            if meta.get("kind") in {"ndvi_index", "ndwi_index"}:
                return {meta.get("kind"): image}
        try:
            payload = json.loads(image)
            if isinstance(payload, dict):
                return payload
        except json.JSONDecodeError:
            pass
        raise ToolExecutionError("image must be an artifact manifest URI, direct index URI, or JSON manifest payload")

    def resolve_index_for_kind(self, *, image: str, kind: str) -> str:
        manifest = self._resolve_manifest(image)
        key = f"{kind}_index"
        direct_meta = self.artifacts.read_meta(image) if image.startswith("artifact://") else {}
        if direct_meta.get("kind") == key:
            return image
        if key in manifest:
            value = manifest[key]
            if isinstance(value, dict):
                return self._resolve_ref(value)
            return str(value)
        raise ToolExecutionError(f"Could not resolve {key} from supplied image payload")

    def render_index(self, *, image: str, kind: str) -> dict[str, Any]:
        index_ref = self.resolve_index_for_kind(image=image, kind=kind)
        arrays = self.artifacts.read_npz(index_ref)
        array = np.asarray(arrays["array"], dtype=np.float32)
        if kind == "ndvi":
            cmap = "RdYlGn"
            threshold = 0.2
        else:
            cmap = "Blues"
            threshold = 0.1
        image_ref = self._plot_array(array, cmap=cmap, label=kind.upper(), namespace=f"remote_sensing/{kind}_map")
        stats = self._index_stats(array, threshold=threshold)
        key = f"{kind}_map"
        return {key: image_ref, "stats": stats, "index_ref": index_ref}

    def desertification_metrics(self, *, image1: str, image2: str) -> tuple[Any, dict[str, Any], dict[str, Any]]:
        manifest1 = self._resolve_manifest(image1)
        manifest2 = self._resolve_manifest(image2)

        ndvi_ref1 = self.resolve_index_for_kind(image=image1, kind="ndvi")
        ndvi_ref2 = self.resolve_index_for_kind(image=image2, kind="ndvi")
        ndwi_ref1 = self.resolve_index_for_kind(image=image1, kind="ndwi")
        ndwi_ref2 = self.resolve_index_for_kind(image=image2, kind="ndwi")

        ndvi1 = np.asarray(self.artifacts.read_npz(ndvi_ref1)["array"], dtype=np.float32)
        ndvi2 = np.asarray(self.artifacts.read_npz(ndvi_ref2)["array"], dtype=np.float32)
        ndwi1 = np.asarray(self.artifacts.read_npz(ndwi_ref1)["array"], dtype=np.float32)
        ndwi2 = np.asarray(self.artifacts.read_npz(ndwi_ref2)["array"], dtype=np.float32)

        h = min(ndvi1.shape[0], ndvi2.shape[0], ndwi1.shape[0], ndwi2.shape[0])
        w = min(ndvi1.shape[1], ndvi2.shape[1], ndwi1.shape[1], ndwi2.shape[1])
        ndvi1 = ndvi1[:h, :w]
        ndvi2 = ndvi2[:h, :w]
        ndwi1 = ndwi1[:h, :w]
        ndwi2 = ndwi2[:h, :w]

        delta_ndvi = ndvi2 - ndvi1
        delta_ndwi = ndwi2 - ndwi1
        valid = np.isfinite(delta_ndvi) & np.isfinite(delta_ndwi)
        if not valid.any():
            raise ToolExecutionError("No valid overlapping pixels for desertification analysis.")

        degraded = valid & (delta_ndvi < -0.12) & (delta_ndwi < -0.05)
        severe = valid & (delta_ndvi < -0.25)
        moisture_loss = valid & (delta_ndwi < -0.10)
        vegetation_gain = valid & (delta_ndvi > 0.10)

        metrics = {
            "valid_pixels": int(valid.sum()),
            "mean_ndvi_delta": float(np.nanmean(delta_ndvi[valid])),
            "mean_ndwi_delta": float(np.nanmean(delta_ndwi[valid])),
            "degraded_fraction": float(degraded.sum() / valid.sum()),
            "severe_fraction": float(severe.sum() / valid.sum()),
            "moisture_loss_fraction": float(moisture_loss.sum() / valid.sum()),
            "vegetation_gain_fraction": float(vegetation_gain.sum() / valid.sum()),
        }
        change_ref = self._plot_array(delta_ndvi, cmap="PiYG", label="Delta NDVI", namespace="remote_sensing/change_map")
        context = {
            "image1": {"date": manifest1.get("date"), "lat": manifest1.get("lat"), "lon": manifest1.get("lon")},
            "image2": {"date": manifest2.get("date"), "lat": manifest2.get("lat"), "lon": manifest2.get("lon")},
            "metrics": metrics,
        }
        return change_ref, metrics, context
