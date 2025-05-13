import { useContext } from 'react';
import { ServicesContext } from '../context/ServicesContext';

export function useServices() {
  const ctx = useContext(ServicesContext);
  if (!ctx) throw new Error('ServicesContext not found');
  return ctx;
}
