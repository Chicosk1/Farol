import { useSyncExternalStore } from 'react';

/** A mesma largura em que o layout.css troca o menu lateral pela barra inferior. */
const CONSULTA = '(max-width: 767px)';

function consulta(): MediaQueryList | undefined {
  return typeof window.matchMedia === 'function' ? window.matchMedia(CONSULTA) : undefined;
}

function acompanhar(aoMudar: () => void): () => void {
  const lista = consulta();
  lista?.addEventListener('change', aoMudar);
  return () => lista?.removeEventListener('change', aoMudar);
}

/** Se a tela é estreita como a de um celular: aí a navegação fica na barra inferior. */
export function useTelaEstreita(): boolean {
  return useSyncExternalStore(
    acompanhar,
    () => consulta()?.matches ?? false,
    () => false,
  );
}
