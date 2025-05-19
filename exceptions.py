class AgentError(Exception):
    """Base class for all agent-related exceptions."""

    pass


class ValidationError(AgentError):
    """Raised when input validation fails."""

    pass


class InputValidationError(ValidationError):
    """Raised when the agent input does not match the expected type."""

    pass


class SchemaValidationError(ValidationError):
    """Raised when output schema validation fails."""

    pass


class ModelUnavailableError(AgentError):
    """Raised when required model is not available."""

    pass


class FileReadError(AgentError):
    """Raised when file reading operations fail."""

    pass


class DirectoryReadError(AgentError):
    """Raised when directory reading operations fail."""

    pass


class AnalysisError(AgentError):
    """Raised when code analysis operations fail."""

    pass


class CompilationError(AgentError):
    """Raised when code compilation fails."""

    pass


class RepairError(AgentError):
    """Raised when code repair fails."""

    pass


class TimeoutError(AgentError):
    """Raised when an operation times out."""

    pass


class FallbackUnavailableError(AgentError):
    """Raised when fallback model is not available."""

    pass


class RetryExhaustedError(AgentError):
    """Raised when retry attempts are exhausted."""

    pass


class ConfigurationError(AgentError):
    """Raised when there is a configuration issue."""

    pass
