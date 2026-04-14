from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class OpenAIConfig(BaseModel):
    api_key: str | None = None
    model: str = "gpt-5"
    reasoning_effort: str = "medium"
    base_url: str | None = None


class TavilyConfig(BaseModel):
    api_key: str | None = None
    max_results: int = 6
    search_url: str = "https://api.tavily.com/search"


class OpenMeteoConfig(BaseModel):
    api_key: str | None = None
    geocoding_url: str = "https://geocoding-api.open-meteo.com/v1/search"
    air_quality_url: str = "https://air-quality-api.open-meteo.com/v1/air-quality"
    weather_url: str = "https://api.open-meteo.com/v1/forecast"
    archive_url: str = "https://archive-api.open-meteo.com/v1/archive"
    flood_url: str = "https://flood-api.open-meteo.com/v1/flood"


class SatelliteConfig(BaseModel):
    buffer_meters: int = 6000
    search_window_days: int = 30
    max_cloud_pct: int = 30
    thumb_size: int = 512
    collection: str = "COPERNICUS/S2_SR_HARMONIZED"


class BirdConfig(BaseModel):
    model_path: Path | None = None
    labels_path: Path | None = None
    top_n: int = 5
    sample_rate: int = 16000
    clip_seconds: int = 10
    n_mfcc: int = 13


class CarbonConfig(BaseModel):
    default_currency: str = "USD"
    ef_currency: str = "EUR"
    ef_year: int = 2019
    fx_to_ef: float = 0.93
    deflator_to_ef_year: float = 0.97


class AgentConfig(BaseModel):
    max_iterations: int = 8
    system_prompt: str = "research/default"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
        populate_by_name=True,
    )

    gca_artifacts_dir: Path = Field(default=Path("./artifacts"), alias="GCA_ARTIFACTS_DIR")
    gca_debug: bool = Field(default=False, alias="GCA_DEBUG")
    gca_http_timeout: int = Field(default=60, alias="GCA_HTTP_TIMEOUT")
    gca_http_retries: int = Field(default=3, alias="GCA_HTTP_RETRIES")
    gca_agent_max_iterations: int = Field(default=8, alias="GCA_AGENT_MAX_ITERATIONS")
    gca_agent_system_prompt: str = Field(default="research/default", alias="GCA_AGENT_SYSTEM_PROMPT")

    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-5", alias="OPENAI_MODEL")
    openai_reasoning_effort: str = Field(default="medium", alias="OPENAI_REASONING_EFFORT")
    openai_base_url: str | None = Field(default=None, alias="OPENAI_BASE_URL")

    tavily_api_key: str | None = Field(default=None, alias="TAVILY_API_KEY")
    tavily_max_results: int = Field(default=6, alias="TAVILY_MAX_RESULTS")
    tavily_search_url: str = Field(default="https://api.tavily.com/search", alias="TAVILY_SEARCH_URL")

    open_meteo_api_key: str | None = Field(default=None, alias="OPEN_METEO_API_KEY")
    open_meteo_geocoding_url: str = Field(default="https://geocoding-api.open-meteo.com/v1/search", alias="OPEN_METEO_GEOCODING_URL")
    open_meteo_air_quality_url: str = Field(default="https://air-quality-api.open-meteo.com/v1/air-quality", alias="OPEN_METEO_AIR_QUALITY_URL")
    open_meteo_weather_url: str = Field(default="https://api.open-meteo.com/v1/forecast", alias="OPEN_METEO_WEATHER_URL")
    open_meteo_archive_url: str = Field(default="https://archive-api.open-meteo.com/v1/archive", alias="OPEN_METEO_ARCHIVE_URL")
    open_meteo_flood_url: str = Field(default="https://flood-api.open-meteo.com/v1/flood", alias="OPEN_METEO_FLOOD_URL")

    earth_engine_project: str | None = Field(default=None, alias="EARTH_ENGINE_PROJECT")
    earth_engine_service_account_email: str | None = Field(default=None, alias="EARTH_ENGINE_SERVICE_ACCOUNT_EMAIL")
    earth_engine_service_account_json: Path | None = Field(default=None, alias="EARTH_ENGINE_SERVICE_ACCOUNT_JSON")

    satellite_buffer_meters: int = Field(default=6000, alias="SATELLITE_BUFFER_METERS")
    satellite_search_window_days: int = Field(default=30, alias="SATELLITE_SEARCH_WINDOW_DAYS")
    satellite_max_cloud_pct: int = Field(default=30, alias="SATELLITE_MAX_CLOUD_PCT")
    satellite_thumb_size: int = Field(default=512, alias="SATELLITE_THUMB_SIZE")
    satellite_collection: str = Field(default="COPERNICUS/S2_SR_HARMONIZED", alias="SATELLITE_COLLECTION")

    bird_model_path: Path | None = Field(default=None, alias="BIRD_MODEL_PATH")
    bird_labels_path: Path | None = Field(default=None, alias="BIRD_LABELS_PATH")
    bird_top_n: int = Field(default=5, alias="BIRD_TOP_N")
    bird_sample_rate: int = Field(default=16000, alias="BIRD_SAMPLE_RATE")
    bird_clip_seconds: int = Field(default=10, alias="BIRD_CLIP_SECONDS")
    bird_n_mfcc: int = Field(default=13, alias="BIRD_N_MFCC")

    bioclip_bin: str = Field(default="bioclip", alias="BIOCLIP_BIN")
    bioclip_top_k: int = Field(default=5, alias="BIOCLIP_TOP_K")

    carbon_default_currency: str = Field(default="USD", alias="CARBON_DEFAULT_CURRENCY")
    carbon_ef_currency: str = Field(default="EUR", alias="CARBON_EF_CURRENCY")
    carbon_ef_year: int = Field(default=2019, alias="CARBON_EF_YEAR")
    carbon_fx_to_ef: float = Field(default=0.93, alias="CARBON_FX_TO_EF")
    carbon_deflator_to_ef_year: float = Field(default=0.97, alias="CARBON_DEFLATOR_TO_EF_YEAR")

    default_pollen_forecast_days: int = Field(default=4, alias="DEFAULT_POLLEN_FORECAST_DAYS")
    default_uv_forecast_days: int = Field(default=7, alias="DEFAULT_UV_FORECAST_DAYS")

    @classmethod
    def load(cls) -> "Settings":
        return cls()

    @property
    def artifacts_path(self) -> Path:
        return self.gca_artifacts_dir.expanduser().resolve()

    @property
    def openai(self) -> OpenAIConfig:
        return OpenAIConfig(
            api_key=self.openai_api_key,
            model=self.openai_model,
            reasoning_effort=self.openai_reasoning_effort,
            base_url=self.openai_base_url,
        )

    @property
    def tavily(self) -> TavilyConfig:
        return TavilyConfig(
            api_key=self.tavily_api_key,
            max_results=self.tavily_max_results,
            search_url=self.tavily_search_url,
        )

    @property
    def open_meteo(self) -> OpenMeteoConfig:
        return OpenMeteoConfig(
            api_key=self.open_meteo_api_key,
            geocoding_url=self.open_meteo_geocoding_url,
            air_quality_url=self.open_meteo_air_quality_url,
            weather_url=self.open_meteo_weather_url,
            archive_url=self.open_meteo_archive_url,
            flood_url=self.open_meteo_flood_url,
        )

    @property
    def satellite(self) -> SatelliteConfig:
        return SatelliteConfig(
            buffer_meters=self.satellite_buffer_meters,
            search_window_days=self.satellite_search_window_days,
            max_cloud_pct=self.satellite_max_cloud_pct,
            thumb_size=self.satellite_thumb_size,
            collection=self.satellite_collection,
        )

    @property
    def birds(self) -> BirdConfig:
        return BirdConfig(
            model_path=self.bird_model_path.expanduser().resolve() if self.bird_model_path else None,
            labels_path=self.bird_labels_path.expanduser().resolve() if self.bird_labels_path else None,
            top_n=self.bird_top_n,
            sample_rate=self.bird_sample_rate,
            clip_seconds=self.bird_clip_seconds,
            n_mfcc=self.bird_n_mfcc,
        )

    @property
    def carbon(self) -> CarbonConfig:
        return CarbonConfig(
            default_currency=self.carbon_default_currency,
            ef_currency=self.carbon_ef_currency,
            ef_year=self.carbon_ef_year,
            fx_to_ef=self.carbon_fx_to_ef,
            deflator_to_ef_year=self.carbon_deflator_to_ef_year,
        )

    @property
    def agent(self) -> AgentConfig:
        return AgentConfig(
            max_iterations=self.gca_agent_max_iterations,
            system_prompt=self.gca_agent_system_prompt,
        )
