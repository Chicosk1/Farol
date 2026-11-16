import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useState, type ReactNode } from 'react';

/** Provedores comuns a todas as telas. Os dados do servidor ficam no TanStack Query (ADR 0007). */
export function Provedores({ children }: { children: ReactNode }) {
  const [clienteDeDados] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: { staleTime: 30_000, retry: 1 },
        },
      }),
  );
  return <QueryClientProvider client={clienteDeDados}>{children}</QueryClientProvider>;
}
