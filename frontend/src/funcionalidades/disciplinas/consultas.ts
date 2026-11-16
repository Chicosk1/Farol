import { keepPreviousData, useQuery } from '@tanstack/react-query';

import { listarDisciplinas, type FiltroDeDisciplinas } from '../../api/cliente';

export function useDisciplinas(busca: string, filtro: FiltroDeDisciplinas = 'todas') {
  return useQuery({
    queryKey: ['disciplinas', { busca: busca.trim(), filtro }],
    queryFn: () => listarDisciplinas({ busca, filtro }),
    // Enquanto a nova busca carrega, a lista anterior continua na tela, sem piscar.
    placeholderData: keepPreviousData,
  });
}
