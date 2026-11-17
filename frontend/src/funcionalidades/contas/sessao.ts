import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import {
  confirmarCienciaDoAviso,
  entrarEmDesenvolvimento,
  obterEu,
  sair,
  type Eu,
} from '../../api/cliente';

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

/** Registra a leitura do aviso de privacidade e libera o uso (ACE-RF-08). */
export function useConfirmarCienciaDoAviso() {
  const clienteDeDados = useQueryClient();
  return useMutation({
    mutationFn: confirmarCienciaDoAviso,
    onSuccess: () =>
      clienteDeDados.setQueryData<Eu | null>(CHAVE_EU, (eu) =>
        eu ? { ...eu, precisa_ver_aviso: false } : eu,
      ),
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
