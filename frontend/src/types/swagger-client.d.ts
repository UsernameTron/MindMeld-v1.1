declare module 'swagger-client' {
  interface SwaggerClient {
    spec: {
      openapi: string;
      info: {
        title: string;
        version: string;
        [key: string]: unknown;
      };
      paths: Record<string, unknown>;
      [key: string]: unknown;
    };
    [key: string]: unknown;
  }

  function Swagger(url: string): Promise<SwaggerClient>;

  export = Swagger;
}
