import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { entrarEmDesenvolvimento, obterEu, sair, type Eu } from '../../api/cliente';

const CHAVE_EU = ['eu'] as const;

/** A pessoa logada: `data` é null quando ninguém entrou e undefined enquanto carrega. */
export function useEu() {
  return useQuery({ queryKey: CHAVE_EU, queryFn: obterEu, retry: false, staleTime: Infinity });
}

export function useEntrarEmDesenvolvimento() {
  const clienteDeDados = useQueryClient();
  return useMutation({
    mutationFn: entrarEmDesenvolvimento,
    onSuccess: (eu: Eu) => clienteDeDados.setQueryData(CHAVE_EU, eu),
  });
}

export function useSair() {
  const clienteDeDados = useQueryClient();
  return useMutation({
    mutationFn: sair,
    onSuccess: () => {
      // Tudo o que estava em cache é da pessoa que saiu.
      clienteDeDados.clear();
      clienteDeDados.setQueryData(CHAVE_EU, null);
    },
  });
}

/** Os atalhos de entrada só existem no servidor de desenvolvimento do Vite (ACE-RNF-03). */
export function loginDeDesenvolvimentoDisponivel(): boolean {
  return import.meta.env.DEV;
}
