import Swagger from 'swagger-client';

/**
 * Type definition for OpenAPI specification
 */
export interface OpenAPISpec {
  openapi: string;
  info: {
    title: string;
    version: string;
    [key: string]: unknown;
  };
  paths: Record<string, unknown>;
  [key: string]: unknown;
}

/**
 * Load and parse an OpenAPI spec from a given URL.
 * @param url - The URL to the OpenAPI JSON or YAML document.
 * @returns Parsed OpenAPI spec object.
 */
export async function loadOpenAPISpec(url: string): Promise<OpenAPISpec> {
  const client = await Swagger(url);
  return client.spec as OpenAPISpec;
}
