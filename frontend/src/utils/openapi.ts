import Swagger from 'swagger-client';

/**
 * Load and parse an OpenAPI spec from a given URL.
 * @param url - The URL to the OpenAPI JSON or YAML document.
 * @returns Parsed OpenAPI spec object.
 */
export async function loadOpenAPISpec(url: string): Promise<any> {
  const client = await Swagger(url);
  return client.spec;
}
