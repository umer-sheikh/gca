from __future__ import annotations

from gulf_climate_agent.contracts.biodiversity import CandidateSpecies, DetectBirdInput, DetectBirdOutput, DetectSpeciesInput, DetectSpeciesOutput
from gulf_climate_agent.tools.base import ToolServices, build_meta, dump_model, make_structured_tool


BIODIVERSITY_DESCRIPTIONS = {
    "detect_bird": "Recognize bird calls from an audio clip and return candidate species with confidence.",
    "detect_species": "Classify plant or animal species from an image using BioCLIP and return candidate species with confidence.",
}


def build_biodiversity_tools(services: ToolServices):
    birds = services.birds
    bioclip = services.bioclip

    def detect_bird(audio_clip: str):
        payload = DetectBirdInput(audio_clip=audio_clip)
        candidates = birds.classify(payload.audio_clip, top_n=services.settings.birds.top_n)
        output = DetectBirdOutput(
            meta=build_meta(provider="tensorflow_audio_classifier", source=str(services.settings.birds.model_path) if services.settings.birds.model_path else None),
            candidates=[CandidateSpecies(**row) for row in candidates],
        )
        return dump_model(output)

    def detect_species(image: str):
        payload = DetectSpeciesInput(image=image)
        candidates = bioclip.classify(payload.image, top_k=services.settings.bioclip_top_k)
        output = DetectSpeciesOutput(
            meta=build_meta(provider="bioclip", source=services.settings.bioclip_bin),
            candidates=[CandidateSpecies(**row) for row in candidates],
        )
        return dump_model(output)

    return [
        make_structured_tool(name="detect_bird", description=BIODIVERSITY_DESCRIPTIONS["detect_bird"], args_schema=DetectBirdInput, fn=detect_bird),
        make_structured_tool(name="detect_species", description=BIODIVERSITY_DESCRIPTIONS["detect_species"], args_schema=DetectSpeciesInput, fn=detect_species),
    ]
