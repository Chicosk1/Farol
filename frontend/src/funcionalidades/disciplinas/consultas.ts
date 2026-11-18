import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import {
  definirFavorito,
  listarDisciplinas,
  obterDisciplina,
  type FiltroDeDisciplinas,
} from '../../api/cliente';

/** Uma disciplina da pessoa, para o cabeçalho das telas da disciplina. */
export function useDisciplina(id: number | string | undefined) {
  return useQuery({
    queryKey: ['disciplinas', 'uma', String(id)],
    queryFn: () => obterDisciplina(id as number | string),
    enabled: id !== undefined,
  });
}

export function useDisciplinas(busca: string, filtro: FiltroDeDisciplinas = 'todas') {
  return useQuery({
    queryKey: ['disciplinas', { busca: busca.trim(), filtro }],
    queryFn: () => listarDisciplinas({ busca, filtro }),
    // Ao digitar, a lista anterior continua na tela enquanto a nova busca carrega, sem piscar.
    // Ao trocar de aba, não: mostrar as "Todas" no lugar das "Favoritas" enganaria.
    placeholderData: (anterior, consultaAnterior) =>
      (consultaAnterior?.queryKey[1] as { filtro?: string } | undefined)?.filtro === filtro
        ? anterior
        : undefined,
  });
}

/** Marca ou desmarca uma disciplina como favorita e recarrega todas as listas de disciplinas. */
export function useDefinirFavorito() {
  const clienteDeDados = useQueryClient();
  return useMutation({
    mutationFn: ({ id, favorita }: { id: number; favorita: boolean }) =>
      definirFavorito(id, favorita),
    onSuccess: () => clienteDeDados.invalidateQueries({ queryKey: ['disciplinas'] }),
  });
}
