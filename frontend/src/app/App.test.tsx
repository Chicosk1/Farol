import { screen } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';

import { ANA, FAVORITAS_VAZIAS, simularApi } from '../testes/api';
import { violacoesDeAcessibilidade } from '../testes/acessibilidade';
import { renderizarApp } from '../testes/renderizar';

describe('aplicação', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('mostra a página inicial com o título Farol dentro do conteúdo principal', async () => {
    simularApi({ 'GET /api/eu': { corpo: ANA }, ...FAVORITAS_VAZIAS });
    renderizarApp('/');

    const titulo = await screen.findByRole('heading', { level: 1, name: 'Farol' });
    expect(screen.getByRole('main')).toContainElement(titulo);
  });

  it('avisa quando a página não existe e oferece o caminho de volta', async () => {
    simularApi({});
    renderizarApp('/endereco-que-nao-existe');

    expect(
      await screen.findByRole('heading', { level: 1, name: 'Página não encontrada' }),
    ).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Voltar para o início' })).toHaveAttribute('href', '/');
  });

  it.each(['/', '/endereco-que-nao-existe'])(
    'não tem violações de acessibilidade em %s',
    async (caminho) => {
      simularApi({ 'GET /api/eu': { corpo: ANA }, ...FAVORITAS_VAZIAS });
      const { container } = renderizarApp(caminho);
      await screen.findByRole('heading', { level: 1 });

      expect(await violacoesDeAcessibilidade(container)).toEqual([]);
    },
  );
});
