import { QueryClientProvider, type QueryClient } from '@tanstack/react-query';
import { useState, type ReactNode } from 'react';

import { ProvedorDeAvisos } from '../componentes/Avisos';
import { criarClienteDeDados } from './clienteDeDados';

/**
 * Provedores comuns a todas as telas. Os dados do servidor ficam no TanStack Query (ADR 0007), e
 * os avisos curtos (toasts) do design system, no ProvedorDeAvisos.
 * Os testes passam o próprio cliente, por exemplo sem tentativas repetidas.
 */
export function Provedores({ children, cliente }: { children: ReactNode; cliente?: QueryClient }) {
  const [clienteDeDados] = useState(() => cliente ?? criarClienteDeDados());
  return (
    <QueryClientProvider client={clienteDeDados}>
      <ProvedorDeAvisos>{children}</ProvedorDeAvisos>
    </QueryClientProvider>
  );
}
