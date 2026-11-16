/** Temas do design system Farol, com os mesmos nomes do protótipo (atributo data-theme no <html>). */
export type Tema = 'light' | 'dark';

const CONSULTA_ESCURO = '(prefers-color-scheme: dark)';

function consultaDoSistema(): MediaQueryList | undefined {
  return typeof window.matchMedia === 'function' ? window.matchMedia(CONSULTA_ESCURO) : undefined;
}

/**
 * Aplica no <html> o tema preferido pelo sistema e acompanha as trocas.
 * Devolve a função que para de acompanhar.
 */
export function aplicarTema(raiz: HTMLElement = document.documentElement): () => void {
  const consulta = consultaDoSistema();
  const definir = (escuro: boolean) => {
    raiz.dataset.theme = escuro ? 'dark' : 'light';
  };

  definir(consulta?.matches ?? false);
  if (!consulta) {
    return () => {};
  }

  const aoMudar = (evento: { matches: boolean }) => definir(evento.matches);
  consulta.addEventListener('change', aoMudar);
  return () => consulta.removeEventListener('change', aoMudar);
}
