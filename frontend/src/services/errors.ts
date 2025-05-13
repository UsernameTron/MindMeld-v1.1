export class ServiceError extends Error {
  constructor(
    public readonly service: string,
    public readonly operation: string,
    message: string,
    public readonly originalError?: unknown
  ) {
    super(`${service} error during ${operation}: ${message}`);
    this.name = 'ServiceError';
  }
}

export function handleServiceError(service: string, operation: string, error: unknown): ServiceError {
  if (error instanceof ServiceError) return error;
  const message = error instanceof Error ? error.message : String(error);
  return new ServiceError(service, operation, message, error);
}
