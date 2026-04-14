from __future__ import annotations

from gulf_climate_agent.contracts.remote_sensing import CalculateNdviInput, CalculateNdwiInput, DesertificationAnalysisInput, DesertificationMetrics, DesertificationOutput, GetSatelliteImageInput, IndexStats, NdviOutput, NdwiOutput, SatelliteImageOutput
from gulf_climate_agent.tools.base import ToolServices, build_meta, dump_model, make_structured_tool


REMOTE_SENSING_DESCRIPTIONS = {
    "get_satellite_image": "Retrieve a multispectral satellite image for a coordinate and date. Returns rgb_img, ndvi_index, ndwi_index, image_ref, and metadata.",
    "calculate_ndvi": "Compute NDVI from an image manifest or NDVI artifact and return ndvi_map plus summary stats.",
    "calculate_ndwi": "Compute NDWI from an image manifest or NDWI artifact and return ndwi_map plus summary stats.",
    "desertification_analysis": "Compare two image manifests, compute change metrics, and synthesize a concise desertification analysis.",
}


def build_remote_sensing_tools(services: ToolServices):
    satellite = services.satellite
    openai_client = services.openai

    def get_satellite_image(lat: float, lon: float, date: str):
        payload = GetSatelliteImageInput(lat=lat, lon=lon, date=date)
        result = satellite.get_satellite_image(lat=payload.lat, lon=payload.lon, date=payload.date)
        output = SatelliteImageOutput(
            meta=build_meta(
                provider="google_earth_engine",
                source=services.settings.satellite.collection,
                units={"ndvi": "dimensionless", "ndwi": "dimensionless"},
                location={"lat": payload.lat, "lon": payload.lon},
                timestamps={"requested_date": payload.date},
            ),
            rgb_img=result["rgb_img"],
            ndvi_index=result["ndvi_index"],
            ndwi_index=result["ndwi_index"],
            image_ref=result["image_ref"],
            metadata=result["metadata"],
        )
        return dump_model(output)

    def calculate_ndvi(image: str):
        payload = CalculateNdviInput(image=image)
        result = satellite.render_index(image=payload.image, kind="ndvi")
        output = NdviOutput(
            meta=build_meta(
                provider="artifact_renderer",
                source=result["index_ref"],
                units={"ndvi": "dimensionless"},
            ),
            ndvi_map=result["ndvi_map"],
            stats=IndexStats(**result["stats"]),
        )
        return dump_model(output)

    def calculate_ndwi(image: str):
        payload = CalculateNdwiInput(image=image)
        result = satellite.render_index(image=payload.image, kind="ndwi")
        output = NdwiOutput(
            meta=build_meta(
                provider="artifact_renderer",
                source=result["index_ref"],
                units={"ndwi": "dimensionless"},
            ),
            ndwi_map=result["ndwi_map"],
            stats=IndexStats(**result["stats"]),
        )
        return dump_model(output)

    def desertification_analysis(image1: str, image2: str):
        payload = DesertificationAnalysisInput(image1=image1, image2=image2)
        change_map, metrics, context = satellite.desertification_metrics(image1=payload.image1, image2=payload.image2)
        analysis = openai_client.desertification_analysis(context)
        output = DesertificationOutput(
            meta=build_meta(
                provider="gpt5_plus_remote_sensing",
                source="google_earth_engine+openai",
                units={"mean_ndvi_delta": "dimensionless", "mean_ndwi_delta": "dimensionless"},
                location={"image1": context.get("image1"), "image2": context.get("image2")},
                timestamps={"image1_date": str(context.get("image1", {}).get("date")), "image2_date": str(context.get("image2", {}).get("date"))},
            ),
            change_map=change_map,
            metrics=DesertificationMetrics(**metrics),
            analysis=analysis,
        )
        return dump_model(output)

    return [
        make_structured_tool(name="get_satellite_image", description=REMOTE_SENSING_DESCRIPTIONS["get_satellite_image"], args_schema=GetSatelliteImageInput, fn=get_satellite_image),
        make_structured_tool(name="calculate_ndvi", description=REMOTE_SENSING_DESCRIPTIONS["calculate_ndvi"], args_schema=CalculateNdviInput, fn=calculate_ndvi),
        make_structured_tool(name="calculate_ndwi", description=REMOTE_SENSING_DESCRIPTIONS["calculate_ndwi"], args_schema=CalculateNdwiInput, fn=calculate_ndwi),
        make_structured_tool(name="desertification_analysis", description=REMOTE_SENSING_DESCRIPTIONS["desertification_analysis"], args_schema=DesertificationAnalysisInput, fn=desertification_analysis),
    ]
