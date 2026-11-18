import { fireEvent, screen, within } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';

import { violacoesDeAcessibilidade } from '../testes/acessibilidade';
import { ANA, CARLOS, DISCIPLINAS, ESTRUTURAS, FAVORITAS_VAZIAS, simularApi } from '../testes/api';
import { renderizarApp } from '../testes/renderizar';

function telaDeCelular() {
  vi.stubGlobal('matchMedia', (consulta: string) => ({
    matches: consulta.includes('max-width'),
    media: consulta,
    addEventListener: () => {},
    removeEventListener: () => {},
  }));
}

describe('casca do protótipo (ACE-T71)', () => {
  afterEach(() => vi.unstubAllGlobals());

  it('o cabeçalho tem a marca, o sino e a conta, e o menu do aluno marca a página atual', async () => {
    simularApi({ 'GET /api/eu': { corpo: ANA }, ...FAVORITAS_VAZIAS });
    renderizarApp('/');

    const marca = await screen.findByRole('link', { name: 'Farol, página inicial' });
    expect(marca).toHaveTextContent('Tutor de estudos');
    expect(screen.getByRole('button', { name: 'Conta de Ana Souza' })).toBeInTheDocument();
    const menu = screen.getByRole('navigation', { name: 'Menu principal' });
    expect(within(menu).getByRole('link', { name: 'Início' })).toHaveAttribute(
      'aria-current',
      'page',
    );
    expect(within(menu).getByRole('link', { name: 'Disciplinas' })).not.toHaveAttribute(
      'aria-current',
    );
    expect(within(menu).getByRole('link', { name: 'Tutor' })).toHaveAttribute('href', '/tutor');
    expect(within(menu).getByRole('link', { name: 'Buscar disciplina' })).toBeInTheDocument();
  });

  it('o menu da conta mostra a pessoa, fecha com Esc e devolve o foco ao avatar', async () => {
    simularApi({ 'GET /api/eu': { corpo: ANA }, ...FAVORITAS_VAZIAS });
    renderizarApp('/');

    const avatar = await screen.findByRole('button', { name: 'Conta de Ana Souza' });
    fireEvent.click(avatar);
    const conta = screen.getByRole('dialog', { name: 'Sua conta' });
    expect(within(conta).getByText(ANA.email)).toBeInTheDocument();
    expect(avatar).toHaveAttribute('aria-expanded', 'true');

    fireEvent.keyDown(within(conta).getByRole('button', { name: 'Sair' }), { key: 'Escape' });
    expect(screen.queryByRole('dialog', { name: 'Sua conta' })).toBeNull();
    expect(avatar).toHaveFocus();
  });

  it('dentro de uma disciplina, o menu do professor mostra a turma e as telas dela', async () => {
    simularApi({
      'GET /api/eu': { corpo: CARLOS },
      'GET /api/disciplinas': { corpo: DISCIPLINAS },
      [`GET /api/disciplinas/${ESTRUTURAS.id}/duvidas`]: { corpo: [] },
    });
    renderizarApp(`/disciplinas/${ESTRUTURAS.id}/duvidas`);

    const menu = await screen.findByRole('navigation', { name: 'Menu principal' });
    expect(await within(menu).findByText(`${ESTRUTURAS.nome} · ${ESTRUTURAS.turma}`)).toBeVisible();
    expect(within(menu).getByRole('link', { name: 'Dúvidas' })).toHaveAttribute(
      'aria-current',
      'page',
    );
    expect(within(menu).getByRole('link', { name: 'Materiais' })).toHaveAttribute(
      'href',
      `/disciplinas/${ESTRUTURAS.id}/materiais`,
    );
    expect(screen.getByRole('link', { name: 'Farol, página inicial' })).toHaveTextContent(
      'Painel do professor',
    );
  });

  it('o botão de menu recolhe o menu lateral', async () => {
    simularApi({ 'GET /api/eu': { corpo: ANA }, ...FAVORITAS_VAZIAS });
    const { container } = renderizarApp('/');

    fireEvent.click(await screen.findByRole('button', { name: 'Recolher menu' }));

    expect(container.querySelector('.app')).toHaveAttribute('data-menu', 'recolhido');
    expect(screen.getByRole('button', { name: 'Abrir menu' })).toHaveAttribute(
      'aria-expanded',
      'false',
    );
  });

  it('no celular, o menu fica na barra inferior', async () => {
    telaDeCelular();
    simularApi({ 'GET /api/eu': { corpo: ANA }, ...FAVORITAS_VAZIAS });
    const { container } = renderizarApp('/');

    const barra = await screen.findByRole('navigation', { name: 'Menu principal' });
    expect(barra).toHaveClass('tabbar');
    expect(container.querySelector('.fr-sidebar')).toBeNull();
    expect(within(barra).getByRole('link', { name: 'Início' })).toHaveAttribute(
      'aria-current',
      'page',
    );
  });

  it('o item Tutor abre o tutor da primeira disciplina com material pronto', async () => {
    simularApi({
      'GET /api/eu': { corpo: ANA },
      'GET /api/disciplinas?filtro=com-tutor': { corpo: [ESTRUTURAS] },
      [`GET /api/disciplinas/${ESTRUTURAS.id}/tutor`]: { status: 503 },
    });
    const { roteador } = renderizarApp('/tutor');

    await vi.waitFor(() =>
      expect(roteador.state.location.pathname).toBe(`/disciplinas/${ESTRUTURAS.id}/tutor`),
    );
  });

  it('sem disciplina com tutor, a página do tutor explica o motivo', async () => {
    simularApi({
      'GET /api/eu': { corpo: ANA },
      'GET /api/disciplinas?filtro=com-tutor': { corpo: [] },
    });
    renderizarApp('/tutor');

    expect(
      await screen.findByRole('heading', { name: 'Nenhum tutor disponível ainda' }),
    ).toBeInTheDocument();
  });

  it('não tem violações de acessibilidade, com o menu da conta aberto', async () => {
    simularApi({ 'GET /api/eu': { corpo: ANA }, ...FAVORITAS_VAZIAS });
    const { container } = renderizarApp('/');
    fireEvent.click(await screen.findByRole('button', { name: 'Conta de Ana Souza' }));

    expect(await violacoesDeAcessibilidade(container)).toEqual([]);
  });
});
