import type { AppProps } from 'next/app';
import { AuthProvider } from '../src/context/AuthContext';
// No global CSS import since the file doesn't exist in that location

export default function App({ Component, pageProps }: AppProps) {
  return (
    <AuthProvider>
      <Component {...pageProps} />
    </AuthProvider>
  );
}