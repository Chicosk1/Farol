import { afterEach, describe, expect, it, vi } from 'vitest';

import { aplicarTema } from './tema';

const CONSULTA_ESCURO = '(prefers-color-scheme: dark)';

/** Simula a preferência de tema do sistema e permite trocá-la, como o navegador faz. */
function simularPreferenciaDoSistema(escuroNoInicio: boolean) {
  let escuro = escuroNoInicio;
  const ouvintes = new Set<(evento: { matches: boolean }) => void>();
  const consulta = {
    get matches() {
      return escuro;
    },
    media: CONSULTA_ESCURO,
    addEventListener: (_tipo: 'change', ouvinte: (evento: { matches: boolean }) => void) =>
      ouvintes.add(ouvinte),
    removeEventListener: (_tipo: 'change', ouvinte: (evento: { matches: boolean }) => void) =>
      ouvintes.delete(ouvinte),
  };
  vi.stubGlobal('matchMedia', (media: string) =>
    media === CONSULTA_ESCURO ? consulta : { ...consulta, matches: false },
  );
  return {
    mudarPara(novoEscuro: boolean) {
      escuro = novoEscuro;
      ouvintes.forEach((ouvinte) => ouvinte({ matches: novoEscuro }));
    },
  };
}

describe('aplicarTema', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
    delete document.documentElement.dataset.theme;
  });

  it('usa o tema escuro quando o sistema prefere o escuro', () => {
    simularPreferenciaDoSistema(true);

    aplicarTema();

    expect(document.documentElement.dataset.theme).toBe('dark');
  });

  it('usa o tema claro quando o sistema prefere o claro', () => {
    simularPreferenciaDoSistema(false);

    aplicarTema();

    expect(document.documentElement.dataset.theme).toBe('light');
  });

  it('usa o tema claro quando o navegador não informa a preferência', () => {
    vi.stubGlobal('matchMedia', undefined);

    aplicarTema();

    expect(document.documentElement.dataset.theme).toBe('light');
  });

  it('acompanha a troca de tema do sistema até parar de acompanhar', () => {
    const sistema = simularPreferenciaDoSistema(false);
    const pararDeAcompanhar = aplicarTema();

    sistema.mudarPara(true);
    expect(document.documentElement.dataset.theme).toBe('dark');

    pararDeAcompanhar();
    sistema.mudarPara(false);
    expect(document.documentElement.dataset.theme).toBe('dark');
  });
});
