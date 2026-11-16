import { render, screen } from '@testing-library/react';
import { createMemoryRouter, RouterProvider } from 'react-router';
import { describe, expect, it } from 'vitest';

import { violacoesDeAcessibilidade } from '../testes/acessibilidade';
import { Provedores } from './provedores';
import { rotas } from './rotas';

function renderizarEm(caminho: string) {
  const roteador = createMemoryRouter(rotas, { initialEntries: [caminho] });
  return render(
    <Provedores>
      <RouterProvider router={roteador} />
    </Provedores>,
  );
}

describe('aplicação', () => {
  it('mostra a página inicial com o título Farol dentro do conteúdo principal', async () => {
    renderizarEm('/');

    const titulo = await screen.findByRole('heading', { level: 1, name: 'Farol' });
    expect(screen.getByRole('main')).toContainElement(titulo);
  });

  it('avisa quando a página não existe e oferece o caminho de volta', async () => {
    renderizarEm('/endereco-que-nao-existe');

    expect(
      await screen.findByRole('heading', { level: 1, name: 'Página não encontrada' }),
    ).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Voltar para o início' })).toHaveAttribute('href', '/');
  });

  it.each(['/', '/endereco-que-nao-existe'])(
    'não tem violações de acessibilidade em %s',
    async (caminho) => {
      const { container } = renderizarEm(caminho);
      await screen.findByRole('heading', { level: 1 });

      expect(await violacoesDeAcessibilidade(container)).toEqual([]);
    },
  );
});
