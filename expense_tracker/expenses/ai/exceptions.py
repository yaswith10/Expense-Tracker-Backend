class AIModuleError(Exception):
    """Base exception for all AI module failures."""


class LLMProviderError(AIModuleError):
    """Raised when the LLM provider returns an error response or is unreachable."""


class LLMRateLimitError(LLMProviderError):
    """Raised when the LLM provider responds with a rate limit error (HTTP 429)."""


class LLMResponseParseError(AIModuleError):
    """Raised when the LLM response cannot be parsed into the expected structure."""


class AIConfigurationError(AIModuleError):
    """Raised at initialisation time when required configuration is absent or invalid."""
