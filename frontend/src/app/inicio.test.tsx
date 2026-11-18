import { fireEvent, screen, waitFor, within } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';

import { violacoesDeAcessibilidade } from '../testes/acessibilidade';
import { ANA, CARLOS, DISCIPLINAS, ESTRUTURAS, simularApi } from '../testes/api';
import { renderizarApp } from '../testes/renderizar';
import { quando } from './datas';

const BANCO = DISCIPLINAS.find((d) => d.nome === 'Banco de Dados I')!;
const HOJE = new Date().toISOString();

describe('início do aluno no formato do protótipo (ACE-T75)', () => {
  afterEach(() => vi.unstubAllGlobals());

  it('cumprimenta pelo primeiro nome, com a data de hoje', async () => {
    simularApi({ 'GET /api/eu': { corpo: ANA } });
    renderizarApp('/');

    expect(await screen.findByRole('heading', { level: 1, name: 'Olá, Ana' })).toBeInTheDocument();
  });

  it('o cartão do tutor abre o tutor da favorita com material pronto', async () => {
    simularApi({
      'GET /api/eu': { corpo: ANA },
      'GET /api/disciplinas?filtro=com-tutor': {
        corpo: [
          { ...BANCO, tem_tutor: true },
          { ...ESTRUTURAS, tem_tutor: true, favorita: true },
        ],
      },
    });
    renderizarApp('/');

    expect(
      await screen.findByRole('heading', { name: 'Tutor de Estruturas de Dados' }),
    ).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Abrir tutor' })).toHaveAttribute(
      'href',
      `/disciplinas/${ESTRUTURAS.id}/tutor`,
    );
  });

  it('sem material pronto, o cartão do tutor explica quando ele começa', async () => {
    simularApi({ 'GET /api/eu': { corpo: ANA } });
    renderizarApp('/');

    expect(await screen.findByText(/O tutor começa a responder/)).toBeInTheDocument();
    expect(screen.queryByRole('link', { name: 'Abrir tutor' })).toBeNull();
  });

  it('as novidades são as notificações mais recentes, com link e data', async () => {
    simularApi({
      'GET /api/eu': { corpo: ANA },
      'GET /api/notificacoes': {
        corpo: {
          nao_lidas: 1,
          notificacoes: [
            {
              id: 1,
              tipo: 'material_pronto',
              texto: 'Aula 5, Pilhas, está pronta para o tutor.',
              link: '/disciplinas/4/materiais',
              lida: false,
              criada_em: HOJE,
            },
          ],
        },
      },
    });
    renderizarApp('/');

    const novidades = await screen.findByRole('region', { name: 'Novidades' });
    expect(
      await within(novidades).findByRole('link', {
        name: 'Aula 5, Pilhas, está pronta para o tutor.',
      }),
    ).toHaveAttribute('href', '/disciplinas/4/materiais');
    expect(within(novidades).getByText(quando(HOJE))).toBeInTheDocument();
  });

  it('mostra até três disciplinas, com as favoritas no topo (cenário 3 da História 2)', async () => {
    simularApi({
      'GET /api/eu': { corpo: ANA },
      'GET /api/disciplinas': {
        corpo: DISCIPLINAS.map((d) => ({ ...d, favorita: d.id === ESTRUTURAS.id })),
      },
    });
    renderizarApp('/');

    const lista = await screen.findByRole('list', { name: 'Suas disciplinas' });
    const itens = within(lista).getAllByRole('listitem');
    expect(itens).toHaveLength(3);
    expect(within(itens[0]!).getByText(/^Estruturas de Dados/)).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Ver todas as disciplinas' })).toHaveAttribute(
      'href',
      '/disciplinas',
    );
  });

  it('sem favoritas, sugere marcar com a estrela', async () => {
    simularApi({ 'GET /api/eu': { corpo: ANA }, 'GET /api/disciplinas': { corpo: DISCIPLINAS } });
    renderizarApp('/');

    expect(await screen.findByText(/Marque as suas favoritas com a estrela/)).toBeInTheDocument();
  });

  it('marcar uma favorita na tela de disciplinas a leva para o topo da tela inicial', async () => {
    let favorita = false;
    simularApi({
      'GET /api/eu': { corpo: ANA },
      'GET /api/disciplinas': () => ({
        corpo: DISCIPLINAS.map((d) => ({ ...d, favorita: d.id === ESTRUTURAS.id && favorita })),
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

    const lista = await screen.findByRole('list', { name: 'Suas disciplinas' });
    expect(
      within(within(lista).getAllByRole('listitem')[0]!).getByText(/^Estruturas/),
    ).toBeVisible();
  });

  it('avisa quando não consegue carregar as disciplinas, sem derrubar a página', async () => {
    simularApi({ 'GET /api/eu': { corpo: ANA }, 'GET /api/disciplinas': { status: 500 } });
    renderizarApp('/');

    expect(await screen.findByRole('alert')).toHaveTextContent(
      'Não foi possível carregar as suas disciplinas.',
    );
    expect(screen.getByRole('heading', { name: 'Novidades' })).toBeInTheDocument();
  });

  it('não tem violações de acessibilidade', async () => {
    simularApi({ 'GET /api/eu': { corpo: ANA }, 'GET /api/disciplinas': { corpo: DISCIPLINAS } });
    const { container } = renderizarApp('/');
    await screen.findByRole('list', { name: 'Suas disciplinas' });

    expect(await violacoesDeAcessibilidade(container)).toEqual([]);
  });
});

describe('início do professor (ACE-T76)', () => {
  it('mostra as turmas que leciona, cada uma com os atalhos de trabalho', async () => {
    simularApi({
      'GET /api/eu': { corpo: CARLOS },
      'GET /api/disciplinas': { corpo: [ESTRUTURAS] },
    });
    renderizarApp('/');

    expect(
      await screen.findByRole('heading', { level: 1, name: 'Olá, Carlos' }),
    ).toBeInTheDocument();
    const turmas = await screen.findByRole('list', { name: 'Suas turmas' });
    for (const atalho of ['Materiais de', 'Dúvidas de', 'Configurar o tutor de']) {
      expect(
        within(turmas).getByRole('link', { name: `${atalho} Estruturas de Dados` }),
      ).toBeInTheDocument();
    }
    expect(within(turmas).queryByRole('button', { name: /^Favoritar/ })).toBeNull();
    expect(screen.queryByRole('heading', { name: /^Tutor/ })).toBeNull();
  });

  it('sem turmas, explica de onde elas vêm', async () => {
    simularApi({ 'GET /api/eu': { corpo: CARLOS } });
    renderizarApp('/');

    expect(await screen.findByRole('heading', { name: 'Nenhuma turma ainda' })).toBeInTheDocument();
  });

  it('não tem violações de acessibilidade', async () => {
    simularApi({
      'GET /api/eu': { corpo: CARLOS },
      'GET /api/disciplinas': { corpo: [ESTRUTURAS] },
    });
    const { container } = renderizarApp('/');
    await screen.findByRole('list', { name: 'Suas turmas' });

    expect(await violacoesDeAcessibilidade(container)).toEqual([]);
  });
});
