from __future__ import annotations


class GulfClimateAgentError(Exception):
    """Base exception for the repository."""


class ConfigurationError(GulfClimateAgentError):
    """Raised when runtime configuration is missing or inconsistent."""


class MissingDependencyError(GulfClimateAgentError):
    """Raised when an optional provider dependency is unavailable."""


class ProviderAPIError(GulfClimateAgentError):
    """Raised when an upstream provider returns an unrecoverable error."""


class ArtifactNotFoundError(GulfClimateAgentError):
    """Raised when an artifact reference cannot be resolved."""


class ToolExecutionError(GulfClimateAgentError):
    """Raised when a tool cannot complete its contract."""
