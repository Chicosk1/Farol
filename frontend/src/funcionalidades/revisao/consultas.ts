import { useQuery } from '@tanstack/react-query';

import { obterRevisaoDeHoje } from '../../api/cliente';

export const CHAVE_DA_REVISAO = ['revisao'] as const;

/** A revisão de hoje, compartilhada pela tela inicial e pela tela da revisão. */
export function useRevisaoDeHoje() {
  return useQuery({ queryKey: CHAVE_DA_REVISAO, queryFn: obterRevisaoDeHoje });
}
