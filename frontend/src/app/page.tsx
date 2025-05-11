'use client';

import { useEffect } from 'react';
import { useRouter } from '@/shims/navigation';

export default function HomePage() {
  const router = useRouter();

  useEffect(() => {
    router.push('/dashboard');
  }, [router]);

  return null;
}
