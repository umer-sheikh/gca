from __future__ import annotations

from gulf_climate_agent.config.settings import Settings
from gulf_climate_agent.core.exceptions import ConfigurationError, MissingDependencyError


class EarthEngineSession:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._initialized = False
        self._ee = None

    def get_ee(self):
        if self._initialized and self._ee is not None:
            return self._ee
        try:
            import ee
        except Exception as exc:
            raise MissingDependencyError("earthengine-api is required for remote sensing tools") from exc

        project = self.settings.earth_engine_project
        service_account_json = self.settings.earth_engine_service_account_json
        service_account_email = self.settings.earth_engine_service_account_email

        try:
            if service_account_json and service_account_email:
                credentials = ee.ServiceAccountCredentials(service_account_email, str(service_account_json))
                if project:
                    ee.Initialize(credentials=credentials, project=project)
                else:
                    ee.Initialize(credentials=credentials)
            else:
                if project:
                    ee.Initialize(project=project)
                else:
                    ee.Initialize()
        except Exception as exc:
            raise ConfigurationError(
                "Earth Engine initialization failed. Authenticate locally or configure service-account env vars."
            ) from exc

        self._ee = ee
        self._initialized = True
        return ee
