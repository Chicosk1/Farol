import { fireEvent, screen, waitFor, within } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';

import { violacoesDeAcessibilidade } from '../../testes/acessibilidade';
import { ANA, DISCIPLINAS, simularApi } from '../../testes/api';
import { renderizarApp } from '../../testes/renderizar';

/** API simulada com estado: favoritar e desfavoritar mudam o que a lista devolve. */
function simularApiDeFavoritos(favoritasNoInicio: number[] = []) {
  const favoritas = new Set(favoritasNoInicio);
  const lista = (soFavoritas: boolean) =>
    DISCIPLINAS.map((d) => ({ ...d, favorita: favoritas.has(d.id) })).filter(
      (d) => !soFavoritas || d.favorita,
    );
  const rotas: Parameters<typeof simularApi>[0] = {
    'GET /api/eu': { corpo: ANA },
    'GET /api/disciplinas': () => ({ corpo: lista(false) }),
    'GET /api/disciplinas?filtro=favoritas': () => ({ corpo: lista(true) }),
  };
  for (const d of DISCIPLINAS) {
    rotas[`PUT /api/disciplinas/${d.id}/favorito`] = () => {
      favoritas.add(d.id);
      return { status: 204 };
    };
    rotas[`DELETE /api/disciplinas/${d.id}/favorito`] = () => {
      favoritas.delete(d.id);
      return { status: 204 };
    };
  }
  return { ...simularApi(rotas), favoritas };
}

const ESTRUTURAS = DISCIPLINAS.find((d) => d.nome === 'Estruturas de Dados')!;

describe('abas e favoritos (ACE-T35)', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('a aba Todas vem selecionada, e a Favoritas está disponível', async () => {
    simularApiDeFavoritos();
    renderizarApp('/disciplinas');

    const todas = await screen.findByRole('tab', { name: 'Todas' });
    expect(todas).toHaveAttribute('aria-selected', 'true');
    expect(screen.getByRole('tab', { name: 'Favoritas' })).toHaveAttribute(
      'aria-selected',
      'false',
    );
    expect(screen.getByRole('tabpanel')).toBeInTheDocument();
  });

  it('marcar uma disciplina como favorita faz ela aparecer na aba Favoritas', async () => {
    const { chamadas } = simularApiDeFavoritos();
    renderizarApp('/disciplinas');

    fireEvent.click(await screen.findByRole('button', { name: 'Favoritar Estruturas de Dados' }));

    await waitFor(() =>
      expect(screen.getByRole('button', { name: 'Favoritar Estruturas de Dados' })).toHaveAttribute(
        'aria-pressed',
        'true',
      ),
    );
    expect(
      chamadas.some(
        (c) => c.metodo === 'PUT' && c.caminho === `/api/disciplinas/${ESTRUTURAS.id}/favorito`,
      ),
    ).toBe(true);

    fireEvent.click(screen.getByRole('tab', { name: 'Favoritas' }));

    const lista = await screen.findByRole('list', { name: 'Disciplinas' });
    expect(within(lista).getAllByRole('listitem')).toHaveLength(1);
    expect(within(lista).getByText('Estruturas de Dados')).toBeInTheDocument();
  });

  it('os botões de favoritar começam desmarcados', async () => {
    simularApiDeFavoritos([ESTRUTURAS.id]);
    renderizarApp('/disciplinas');

    expect(
      await screen.findByRole('button', { name: 'Favoritar Estruturas de Dados' }),
    ).toHaveAttribute('aria-pressed', 'true');
    expect(screen.getByRole('button', { name: 'Favoritar Banco de Dados I' })).toHaveAttribute(
      'aria-pressed',
      'false',
    );
  });

  it('desmarcar tira a disciplina da aba Favoritas', async () => {
    const { chamadas } = simularApiDeFavoritos([ESTRUTURAS.id]);
    renderizarApp('/disciplinas');
    fireEvent.click(await screen.findByRole('tab', { name: 'Favoritas' }));

    fireEvent.click(await screen.findByRole('button', { name: 'Favoritar Estruturas de Dados' }));

    expect(await screen.findByText(/Você ainda não tem disciplinas favoritas/)).toBeInTheDocument();
    expect(chamadas.some((c) => c.metodo === 'DELETE')).toBe(true);
  });

  it('na aba Favoritas vazia, ensina a usar a estrela', async () => {
    simularApiDeFavoritos();
    renderizarApp('/disciplinas');

    fireEvent.click(await screen.findByRole('tab', { name: 'Favoritas' }));

    expect(await screen.findByText(/Você ainda não tem disciplinas favoritas/)).toBeInTheDocument();
    expect(screen.queryByText('Nenhuma disciplina encontrada.')).not.toBeInTheDocument();
  });

  it('a busca vale dentro da aba escolhida', async () => {
    const { chamadas } = simularApi({
      'GET /api/eu': { corpo: ANA },
      'GET /api/disciplinas': { corpo: DISCIPLINAS },
      'GET /api/disciplinas?filtro=favoritas': { corpo: [] },
      'GET /api/disciplinas?busca=banco&filtro=favoritas': { corpo: [] },
    });
    renderizarApp('/disciplinas');
    fireEvent.click(await screen.findByRole('tab', { name: 'Favoritas' }));
    fireEvent.change(screen.getByRole('searchbox', { name: 'Buscar disciplina' }), {
      target: { value: 'banco' },
    });

    await waitFor(() =>
      expect(
        chamadas.some((c) => c.caminho === '/api/disciplinas?busca=banco&filtro=favoritas'),
      ).toBe(true),
    );
  });

  it('as setas do teclado trocam de aba, como no padrão ARIA de abas', async () => {
    simularApiDeFavoritos();
    renderizarApp('/disciplinas');
    const todas = await screen.findByRole('tab', { name: 'Todas' });

    fireEvent.keyDown(todas, { key: 'ArrowRight' });

    const favoritas = screen.getByRole('tab', { name: 'Favoritas' });
    expect(favoritas).toHaveAttribute('aria-selected', 'true');
    expect(favoritas).toHaveFocus();
    expect(todas).toHaveAttribute('tabindex', '-1');

    fireEvent.keyDown(favoritas, { key: 'ArrowLeft' });
    expect(screen.getByRole('tab', { name: 'Todas' })).toHaveAttribute('aria-selected', 'true');
  });

  it('avisa quando não consegue atualizar o favorito', async () => {
    simularApi({
      'GET /api/eu': { corpo: ANA },
      'GET /api/disciplinas': { corpo: DISCIPLINAS },
      [`PUT /api/disciplinas/${ESTRUTURAS.id}/favorito`]: { status: 403 },
    });
    renderizarApp('/disciplinas');

    fireEvent.click(await screen.findByRole('button', { name: 'Favoritar Estruturas de Dados' }));

    expect(await screen.findByRole('alert')).toHaveTextContent(
      'Não foi possível atualizar o favorito.',
    );
  });

  it('não tem violações de acessibilidade com as abas e os botões', async () => {
    simularApiDeFavoritos([ESTRUTURAS.id]);
    const { container } = renderizarApp('/disciplinas');
    await screen.findByRole('list', { name: 'Disciplinas' });

    expect(await violacoesDeAcessibilidade(container)).toEqual([]);
  });
});
