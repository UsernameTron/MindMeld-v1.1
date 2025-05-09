'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';
import { loadOpenAPISpec, OpenAPISpec } from '../utils/openapi';

export interface OpenAPIContextType {
  spec: OpenAPISpec | null;
}

const OpenAPIContext = createContext<OpenAPIContextType>({ spec: null });

export const OpenAPIProvider: React.FC<{ url: string; children: React.ReactNode }> = ({
  url,
  children,
}) => {
  const [spec, setSpec] = useState<OpenAPISpec | null>(null);

  useEffect(() => {
    loadOpenAPISpec(url).then(setSpec).catch(console.error);
  }, [url]);

  return <OpenAPIContext.Provider value={{ spec }}>{children}</OpenAPIContext.Provider>;
};

export const useOpenAPI = (): OpenAPIContextType => useContext(OpenAPIContext);
