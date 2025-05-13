import { createContext, useMemo } from 'react';
import { createTTSService, TTSService } from '../services/ttsService';

interface ServicesContextType {
  ttsService: TTSService;
}

interface ServicesProviderProps {
  children: React.ReactNode;
  apiClient: any;
}

const ServicesContext = createContext<ServicesContextType | undefined>(undefined);

export function ServicesProvider({ children, apiClient }: ServicesProviderProps) {
  const services = useMemo(() => ({
    ttsService: createTTSService(apiClient),
  }), [apiClient]);

  return (
    <ServicesContext.Provider value={services}>
      {children}
    </ServicesContext.Provider>
  );
}

export { ServicesContext };
