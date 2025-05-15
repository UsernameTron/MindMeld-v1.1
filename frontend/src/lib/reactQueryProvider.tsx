'use client';
import React, { useRef } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

export function ReactQueryProvider({ children }: { children: React.ReactNode }) {
  const queryClientRef = useRef<QueryClient | undefined>(undefined);
  if (!queryClientRef.current) {
    queryClientRef.current = new QueryClient();
  }
  return <QueryClientProvider client={queryClientRef.current}>{children}</QueryClientProvider>;
}
