class AgentError(Exception):
    """Base class for all agent-related exceptions."""


class ValidationError(AgentError):
    """Raised when input validation fails."""


class InputValidationError(ValidationError):
    """Raised when the agent input does not match the expected type."""


class SchemaValidationError(ValidationError):
    """Raised when output schema validation fails."""


class ModelUnavailableError(AgentError):
    """Raised when required model is not available."""


class FileReadError(AgentError):
    """Raised when file reading operations fail."""


class DirectoryReadError(AgentError):
    """Raised when directory reading operations fail."""


class AnalysisError(AgentError):
    """Raised when code analysis operations fail."""


class CompilationError(AgentError):
    """Raised when code compilation fails."""


class RepairError(AgentError):
    """Raised when code repair fails."""


class TimeoutError(AgentError):
    """Raised when an operation times out."""


class FallbackUnavailableError(AgentError):
    """Raised when fallback model is not available."""


class RetryExhaustedError(AgentError):
    """Raised when retry attempts are exhausted."""


class ConfigurationError(AgentError):
    """Raised when there is a configuration issue."""
