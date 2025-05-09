'use client';

import { useEffect } from 'react';
import { useOpenAPI } from '../../context/OpenAPIContext';

export default function OpenAPIDebug() {
  const spec = useOpenAPI();

  useEffect(() => {
    if (spec) {
      console.log('OpenAPI Paths:', Object.keys(spec.paths || {}));
      console.log('Schemas:', Object.keys(spec.components?.schemas || {}));
    }
  }, [spec]);

  return null;
}
