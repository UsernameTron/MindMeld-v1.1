import React, { createContext, useContext, useEffect, useState } from 'react';
import { loadOpenAPISpec } from '../utils/openapi';

const OpenAPIContext = createContext<any>(null);

export const OpenAPIProvider: React.FC<{ url: string; children: React.ReactNode }> = ({ url, children }) => {
  const [spec, setSpec] = useState<any>(null);

  useEffect(() => {
    loadOpenAPISpec(url).then(setSpec).catch(console.error);
  }, [url]);

  return (
    <OpenAPIContext.Provider value={spec}>
      {children}
    </OpenAPIContext.Provider>
  );
};

export const useOpenAPI = () => useContext(OpenAPIContext);
