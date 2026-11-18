import { fireEvent, screen, waitFor, within } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';

import { violacoesDeAcessibilidade } from '../../testes/acessibilidade';
import { ANA, CARLOS, DISCIPLINAS, simularApi } from '../../testes/api';
import { renderizarApp } from '../../testes/renderizar';

describe('tela de disciplinas (ACE-T33)', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('o cabeçalho leva da página inicial para as disciplinas', async () => {
    simularApi({ 'GET /api/eu': { corpo: ANA }, 'GET /api/disciplinas': { corpo: DISCIPLINAS } });
    const { roteador } = renderizarApp('/');

    fireEvent.click(await screen.findByRole('link', { name: 'Disciplinas' }));

    expect(
      await screen.findByRole('heading', { level: 1, name: 'Disciplinas' }),
    ).toBeInTheDocument();
    expect(roteador.state.location.pathname).toBe('/disciplinas');
  });

  it('mostra as 6 disciplinas, cada uma com código, turma e professor', async () => {
    simularApi({ 'GET /api/eu': { corpo: ANA }, 'GET /api/disciplinas': { corpo: DISCIPLINAS } });
    renderizarApp('/disciplinas');

    const lista = await screen.findByRole('list', { name: 'Disciplinas' });
    const itens = within(lista).getAllByRole('listitem');
    expect(itens).toHaveLength(6);
    expect(within(itens[3]!).getByText(/^Estruturas de Dados/)).toBeInTheDocument();
    expect(within(itens[3]!).getByText(/SINF201/)).toBeInTheDocument();
    expect(within(itens[3]!).getAllByText(/SINF2NA/).length).toBeGreaterThan(0);
    expect(within(itens[3]!).getByText(/Carlos Mendes/)).toBeInTheDocument();
    expect(screen.getByText('6 disciplinas')).toHaveAttribute('role', 'status');
  });

  it('busca pelo nome: envia o texto digitado e mostra só o que a API devolve', async () => {
    const { chamadas } = simularApi({
      'GET /api/eu': { corpo: ANA },
      'GET /api/disciplinas': { corpo: DISCIPLINAS },
      'GET /api/disciplinas?busca=estruturas': { corpo: [DISCIPLINAS[3]] },
    });
    renderizarApp('/disciplinas');
    await screen.findByRole('list', { name: 'Disciplinas' });

    fireEvent.change(screen.getByRole('searchbox', { name: 'Buscar disciplina' }), {
      target: { value: 'estruturas' },
    });

    await waitFor(() => expect(screen.getAllByRole('listitem')).toHaveLength(1));
    expect(screen.getByText(/^Estruturas de Dados/)).toBeInTheDocument();
    expect(await screen.findByText('1 disciplina')).toHaveAttribute('role', 'status');
    expect(chamadas.some((c) => c.caminho === '/api/disciplinas?busca=estruturas')).toBe(true);
  });

  it('busca sem resultado avisa que nada foi encontrado', async () => {
    simularApi({
      'GET /api/eu': { corpo: ANA },
      'GET /api/disciplinas': { corpo: DISCIPLINAS },
      'GET /api/disciplinas?busca=culinaria': { corpo: [] },
    });
    renderizarApp('/disciplinas');
    await screen.findByRole('list', { name: 'Disciplinas' });

    fireEvent.change(screen.getByRole('searchbox', { name: 'Buscar disciplina' }), {
      target: { value: 'culinaria' },
    });

    expect(
      await screen.findByRole('heading', { name: 'Nenhuma disciplina encontrada' }),
    ).toBeInTheDocument();
    expect(screen.queryByRole('list', { name: 'Disciplinas' })).not.toBeInTheDocument();
  });

  it('sem nenhuma disciplina, explica como pedir ajuda', async () => {
    simularApi({ 'GET /api/eu': { corpo: ANA }, 'GET /api/disciplinas': { corpo: [] } });
    renderizarApp('/disciplinas');

    expect(
      await screen.findByRole('heading', { name: 'Nenhuma disciplina encontrada' }),
    ).toBeInTheDocument();
  });

  it('alterna entre grade e lista, e o botão ativo avisa o leitor de tela', async () => {
    simularApi({ 'GET /api/eu': { corpo: ANA }, 'GET /api/disciplinas': { corpo: DISCIPLINAS } });
    renderizarApp('/disciplinas');
    const lista = await screen.findByRole('list', { name: 'Disciplinas' });
    const grade = screen.getByRole('button', { name: 'Ver em grade' });
    const emLista = screen.getByRole('button', { name: 'Ver em lista' });

    expect(lista).toHaveAttribute('data-visao', 'grade');
    expect(grade).toHaveAttribute('aria-pressed', 'true');
    expect(emLista).toHaveAttribute('aria-pressed', 'false');

    fireEvent.click(emLista);

    expect(lista).toHaveAttribute('data-visao', 'lista');
    expect(grade).toHaveAttribute('aria-pressed', 'false');
    expect(emLista).toHaveAttribute('aria-pressed', 'true');
  });

  it('avisa quando não consegue carregar', async () => {
    simularApi({ 'GET /api/eu': { corpo: ANA }, 'GET /api/disciplinas': { status: 500 } });
    renderizarApp('/disciplinas');

    expect(await screen.findByRole('alert')).toHaveTextContent(
      'Não foi possível carregar as disciplinas.',
    );
  });

  it('quem não entrou é levado para a tela de entrada', async () => {
    simularApi({ 'GET /api/eu': { status: 401 } });
    const { roteador } = renderizarApp('/disciplinas');

    await waitFor(() => expect(roteador.state.location.pathname).toBe('/entrar'));
  });

  it('a aba Com tutor mostra só as disciplinas que a API devolve com material pronto', async () => {
    simularApi({
      'GET /api/eu': { corpo: ANA },
      'GET /api/disciplinas': { corpo: DISCIPLINAS },
      'GET /api/disciplinas?filtro=com-tutor': { corpo: [DISCIPLINAS[3]] },
    });
    renderizarApp('/disciplinas');

    fireEvent.click(await screen.findByRole('tab', { name: 'Com tutor' }));

    await waitFor(() => expect(screen.getAllByRole('listitem')).toHaveLength(1));
    expect(screen.getByText(/^Estruturas de Dados/)).toBeInTheDocument();
  });

  it('na aba Com tutor sem nenhuma disciplina pronta, explica o motivo', async () => {
    simularApi({
      'GET /api/eu': { corpo: ANA },
      'GET /api/disciplinas': { corpo: DISCIPLINAS },
      'GET /api/disciplinas?filtro=com-tutor': { corpo: [] },
    });
    renderizarApp('/disciplinas');

    fireEvent.click(await screen.findByRole('tab', { name: 'Com tutor' }));

    expect(await screen.findByText(/material pronto para o tutor/)).toBeInTheDocument();
  });

  it('não tem violações de acessibilidade', async () => {
    simularApi({ 'GET /api/eu': { corpo: ANA }, 'GET /api/disciplinas': { corpo: DISCIPLINAS } });
    const { container } = renderizarApp('/disciplinas');
    await screen.findByRole('list', { name: 'Disciplinas' });

    expect(await violacoesDeAcessibilidade(container)).toEqual([]);
  });

  it('o cartão mostra o atalho do tutor só quando a disciplina tem material pronto (ACE-T74)', async () => {
    const comTutor = DISCIPLINAS.map((d) => ({ ...d, tem_tutor: d.codigo === 'SINF201' }));
    simularApi({ 'GET /api/eu': { corpo: ANA }, 'GET /api/disciplinas': { corpo: comTutor } });
    renderizarApp('/disciplinas');

    const itens = within(await screen.findByRole('list', { name: 'Disciplinas' })).getAllByRole(
      'listitem',
    );
    expect(within(itens[3]!).getByText('Com tutor')).toBeInTheDocument();
    expect(
      within(itens[3]!).getByRole('link', { name: 'Tutor de Estruturas de Dados' }),
    ).toBeInTheDocument();
    expect(within(itens[1]!).queryByRole('link', { name: /^Tutor de/ })).toBeNull();
    expect(
      within(itens[3]!).getByRole('heading', { level: 2, name: 'Estruturas de Dados (SINF201)' }),
    ).toBeInTheDocument();
  });

  it('o professor tem os atalhos de materiais, dúvidas e configuração em cada cartão', async () => {
    simularApi({
      'GET /api/eu': { corpo: CARLOS },
      'GET /api/disciplinas': { corpo: [DISCIPLINAS[3]] },
    });
    renderizarApp('/disciplinas');

    for (const nome of ['Materiais de', 'Dúvidas de', 'Configurar o tutor de']) {
      expect(
        await screen.findByRole('link', { name: `${nome} Estruturas de Dados` }),
      ).toBeInTheDocument();
    }
    expect(screen.queryByRole('link', { name: 'Tutor de Estruturas de Dados' })).toBeNull();
  });

  it('no modo lista, cada disciplina é uma linha que leva à página dela', async () => {
    simularApi({ 'GET /api/eu': { corpo: ANA }, 'GET /api/disciplinas': { corpo: DISCIPLINAS } });
    const { container } = renderizarApp('/disciplinas');
    await screen.findByRole('list', { name: 'Disciplinas' });

    fireEvent.click(screen.getByRole('button', { name: 'Ver em lista' }));

    const linha = screen.getByRole('link', { name: /Estruturas de Dados \(SINF201\)/ });
    expect(linha).toHaveClass('course-row');
    expect(linha).toHaveAttribute('href', `/disciplinas/${DISCIPLINAS[3]!.id}`);
    expect(await violacoesDeAcessibilidade(container)).toEqual([]);
  });
});
