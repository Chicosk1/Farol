import { useQuery } from '@tanstack/react-query';

import { obterTutor } from '../../api/cliente';

/**
 * O tutor da disciplina ao abrir a tela. Não recarrega sozinho: as perguntas desta visita ficam na
 * tela, e recarregar mostraria a conversa guardada repetida.
 */
export function useTutor(disciplinaId: number) {
  return useQuery({
    queryKey: ['tutor', disciplinaId],
    queryFn: () => obterTutor(disciplinaId),
    staleTime: Infinity,
    refetchOnWindowFocus: false,
  });
}
