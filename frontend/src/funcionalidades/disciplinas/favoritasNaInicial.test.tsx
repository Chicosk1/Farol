import { fireEvent, screen, within, waitFor } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';

import { violacoesDeAcessibilidade } from '../../testes/acessibilidade';
import { ANA, DISCIPLINAS, simularApi } from '../../testes/api';
import { renderizarApp } from '../../testes/renderizar';

const ESTRUTURAS = DISCIPLINAS.find((d) => d.nome === 'Estruturas de Dados')!;
const BANCO = DISCIPLINAS.find((d) => d.nome === 'Banco de Dados I')!;

describe('favoritas na tela inicial (ACE-T36)', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('mostra no topo as disciplinas favoritas, com o link para todas', async () => {
    simularApi({
      'GET /api/eu': { corpo: ANA },
      'GET /api/disciplinas?filtro=favoritas': {
        corpo: [
          { ...BANCO, favorita: true },
          { ...ESTRUTURAS, favorita: true },
        ],
      },
    });
    renderizarApp('/');

    const lista = await screen.findByRole('list', { name: 'Disciplinas favoritas' });
    const itens = within(lista).getAllByRole('listitem');
    expect(itens).toHaveLength(2);
    expect(within(itens[0]!).getByText('Banco de Dados I')).toBeInTheDocument();
    expect(within(itens[1]!).getByText(/Carlos Mendes/)).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Ver todas as disciplinas' })).toHaveAttribute(
      'href',
      '/disciplinas',
    );
  });

  it('as favoritas vêm antes dos dados da sessão, no topo da página', async () => {
    simularApi({
      'GET /api/eu': { corpo: ANA },
      'GET /api/disciplinas?filtro=favoritas': { corpo: [{ ...ESTRUTURAS, favorita: true }] },
    });
    renderizarApp('/');

    const favoritas = await screen.findByRole('region', { name: 'Suas disciplinas favoritas' });
    const sessao = screen.getByRole('region', { name: 'Sessão' });

    expect(
      favoritas.compareDocumentPosition(sessao) & Node.DOCUMENT_POSITION_FOLLOWING,
    ).toBeTruthy();
  });

  it('sem favoritas, explica como marcar e leva para as disciplinas', async () => {
    simularApi({
      'GET /api/eu': { corpo: ANA },
      'GET /api/disciplinas?filtro=favoritas': { corpo: [] },
    });
    renderizarApp('/');

    expect(await screen.findByText(/Você ainda não marcou favoritas/)).toBeInTheDocument();
    expect(screen.queryByRole('list', { name: 'Disciplinas favoritas' })).not.toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Ver todas as disciplinas' })).toBeInTheDocument();
  });

  it('marcar uma disciplina na tela de disciplinas faz ela aparecer na tela inicial', async () => {
    let favorita = false;
    simularApi({
      'GET /api/eu': { corpo: ANA },
      'GET /api/disciplinas': () => ({
        corpo: DISCIPLINAS.map((d) => ({ ...d, favorita: d.id === ESTRUTURAS.id && favorita })),
      }),
      'GET /api/disciplinas?filtro=favoritas': () => ({
        corpo: favorita ? [{ ...ESTRUTURAS, favorita: true }] : [],
      }),
      [`PUT /api/disciplinas/${ESTRUTURAS.id}/favorito`]: () => {
        favorita = true;
        return { status: 204 };
      },
    });
    renderizarApp('/disciplinas');

    fireEvent.click(await screen.findByRole('button', { name: 'Favoritar Estruturas de Dados' }));
    await waitFor(() =>
      expect(screen.getByRole('button', { name: 'Favoritar Estruturas de Dados' })).toHaveAttribute(
        'aria-pressed',
        'true',
      ),
    );
    fireEvent.click(screen.getByRole('link', { name: 'Início' }));

    const lista = await screen.findByRole('list', { name: 'Disciplinas favoritas' });
    expect(within(lista).getByText('Estruturas de Dados')).toBeInTheDocument();
  });

  it('avisa quando não consegue carregar as favoritas, sem derrubar a página', async () => {
    simularApi({
      'GET /api/eu': { corpo: ANA },
      'GET /api/disciplinas?filtro=favoritas': { status: 500 },
    });
    renderizarApp('/');

    expect(await screen.findByRole('alert')).toHaveTextContent(
      'Não foi possível carregar as disciplinas favoritas.',
    );
    expect(screen.getByRole('heading', { level: 1, name: 'Farol' })).toBeInTheDocument();
  });

  it('não tem violações de acessibilidade', async () => {
    simularApi({
      'GET /api/eu': { corpo: ANA },
      'GET /api/disciplinas?filtro=favoritas': { corpo: [{ ...ESTRUTURAS, favorita: true }] },
    });
    const { container } = renderizarApp('/');
    await screen.findByRole('list', { name: 'Disciplinas favoritas' });

    expect(await violacoesDeAcessibilidade(container)).toEqual([]);
  });
});
