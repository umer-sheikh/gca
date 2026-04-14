from __future__ import annotations

from pydantic import BaseModel

from gulf_climate_agent.contracts.base import ClimateToolOutput


class CandidateSpecies(BaseModel):
    species: str
    confidence: float


class DetectBirdInput(BaseModel):
    audio_clip: str


class DetectBirdOutput(ClimateToolOutput):
    candidates: list[CandidateSpecies]


class DetectSpeciesInput(BaseModel):
    image: str


class DetectSpeciesOutput(ClimateToolOutput):
    candidates: list[CandidateSpecies]
