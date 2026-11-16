import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { definirFavorito, listarDisciplinas, type FiltroDeDisciplinas } from '../../api/cliente';

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
