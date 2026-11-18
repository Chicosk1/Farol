import { describe, expect, it } from 'vitest';

import { MANIFESTO, OPCOES_DO_WORKBOX } from './pwa';

describe('PWA (ACE-T60)', () => {
  it('o manifesto deixa instalar o Farol na tela inicial, em português', () => {
    expect(MANIFESTO).toMatchObject({
      name: 'Farol',
      short_name: 'Farol',
      lang: 'pt-BR',
      start_url: '/',
      display: 'standalone',
    });
    const tamanhos = MANIFESTO.icons.map((icone) => icone.sizes);
    expect(tamanhos).toEqual(expect.arrayContaining(['192x192', '512x512']));
    expect(MANIFESTO.icons.some((icone) => icone.purpose === 'maskable')).toBe(true);
  });

  it('o service worker não guarda nem intercepta a API, o login e o painel administrativo', () => {
    const fora = OPCOES_DO_WORKBOX.navigateFallbackDenylist;
    for (const caminho of [
      '/api/eu',
      '/api/disciplinas/4/tutor',
      '/admin/',
      '/media/x.pdf',
      '/contas/google/login/callback/',
    ]) {
      expect(fora.some((regra) => regra.test(caminho))).toBe(true);
    }
    expect(fora.some((regra) => regra.test('/disciplinas/4/tutor'))).toBe(false);
    expect(OPCOES_DO_WORKBOX.runtimeCaching).toEqual([]);
  });
});
