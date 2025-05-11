import { lightTheme, darkTheme } from './theme.js';

export type ThemeMode = 'light' | 'dark';

export const getTheme = (mode: ThemeMode = 'light') => {
  return mode === 'light' ? lightTheme : darkTheme;
};

export const getTokenValue = (
  path: string, 
  mode: ThemeMode = 'light'
) => {
  const theme = getTheme(mode);
  const parts = path.split('.');
  
  let result = theme as any;
  for (const part of parts) {
    if (result && part in result) {
      result = result[part];
    } else {
      return undefined;
    }
  }
  
  return result;
};
