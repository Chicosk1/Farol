import { fireEvent, screen, waitFor } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';

import { violacoesDeAcessibilidade } from '../../testes/acessibilidade';
import { ANA, CARLOS, FAVORITAS_VAZIAS, simularApi } from '../../testes/api';
import { renderizarApp } from '../../testes/renderizar';

const SEM_SESSAO = { status: 401, corpo: { detail: 'Credenciais não foram fornecidas.' } };

describe('entrada e sessão (ACE-T26)', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
    vi.unstubAllEnvs();
  });

  it('quem não entrou é levado da página inicial para a tela de entrada', async () => {
    simularApi({ 'GET /api/eu': SEM_SESSAO });
    const { roteador } = renderizarApp('/');

    expect(
      await screen.findByRole('heading', { level: 1, name: 'Entrar no Farol' }),
    ).toBeInTheDocument();
    expect(roteador.state.location.pathname).toBe('/entrar');
  });

  it('em desenvolvimento, oferece entrar como aluna e como professor', async () => {
    simularApi({ 'GET /api/eu': SEM_SESSAO });
    renderizarApp('/entrar');

    expect(await screen.findByRole('button', { name: 'Entrar como aluna' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Entrar como professor' })).toBeInTheDocument();
  });

  it('fora do desenvolvimento, os botões de atalho não existem (ACE-RNF-03)', async () => {
    vi.stubEnv('DEV', false);
    simularApi({ 'GET /api/eu': SEM_SESSAO });
    renderizarApp('/entrar');

    await screen.findByRole('heading', { level: 1, name: 'Entrar no Farol' });
    expect(screen.queryByRole('button', { name: /Entrar como/ })).not.toBeInTheDocument();
  });

  it('entrar como aluna abre a sessão da Ana e leva à página inicial', async () => {
    const { chamadas } = simularApi({
      'GET /api/eu': SEM_SESSAO,
      'POST /api/dev/entrar': { corpo: ANA },
    });
    const { roteador } = renderizarApp('/entrar');

    fireEvent.click(await screen.findByRole('button', { name: 'Entrar como aluna' }));

    await waitFor(() => expect(roteador.state.location.pathname).toBe('/'));
    expect(await screen.findByText('Olá, Ana Souza')).toBeInTheDocument();
    expect(chamadas.find((c) => c.metodo === 'POST')?.corpo).toEqual({ email: ANA.email });
  });

  it('entrar como professor usa o e-mail do Carlos', async () => {
    const { chamadas } = simularApi({
      'GET /api/eu': SEM_SESSAO,
      'POST /api/dev/entrar': { corpo: CARLOS },
    });
    renderizarApp('/entrar');

    fireEvent.click(await screen.findByRole('button', { name: 'Entrar como professor' }));

    expect(await screen.findByText('Olá, Carlos Mendes')).toBeInTheDocument();
    expect(chamadas.find((c) => c.metodo === 'POST')?.corpo).toEqual({ email: CARLOS.email });
  });

  it('avisa quando a entrada falha, sem sair da tela', async () => {
    simularApi({
      'GET /api/eu': SEM_SESSAO,
      'POST /api/dev/entrar': {
        status: 400,
        corpo: { email: ['Não há pessoa ativa com este e-mail.'] },
      },
    });
    renderizarApp('/entrar');

    fireEvent.click(await screen.findByRole('button', { name: 'Entrar como aluna' }));

    expect(await screen.findByRole('alert')).toHaveTextContent(
      'Não foi possível entrar. Rode o comando popular_demo e tente de novo.',
    );
    expect(screen.getByRole('heading', { level: 1, name: 'Entrar no Farol' })).toBeInTheDocument();
  });

  it('quem já entrou e abre a tela de entrada vai direto para a página inicial', async () => {
    simularApi({ 'GET /api/eu': { corpo: ANA }, ...FAVORITAS_VAZIAS });
    const { roteador } = renderizarApp('/entrar');

    await waitFor(() => expect(roteador.state.location.pathname).toBe('/'));
  });

  it('a página inicial mostra a pessoa e o perfil em uso', async () => {
    simularApi({ 'GET /api/eu': { corpo: ANA }, ...FAVORITAS_VAZIAS });
    renderizarApp('/');

    expect(await screen.findByText('Olá, Ana Souza')).toBeInTheDocument();
    expect(screen.getByText('Perfil: aluno')).toBeInTheDocument();
  });

  it('sair encerra a sessão e volta para a tela de entrada', async () => {
    const { chamadas } = simularApi({
      'GET /api/eu': { corpo: ANA },
      ...FAVORITAS_VAZIAS,
      'POST /api/sair': { status: 204 },
    });
    const { roteador } = renderizarApp('/');

    fireEvent.click(await screen.findByRole('button', { name: 'Sair' }));

    await waitFor(() => expect(roteador.state.location.pathname).toBe('/entrar'));
    expect(chamadas.some((c) => c.metodo === 'POST' && c.caminho === '/api/sair')).toBe(true);
  });

  it.each(['/entrar', '/'])('não tem violações de acessibilidade em %s', async (caminho) => {
    simularApi({ 'GET /api/eu': caminho === '/' ? { corpo: ANA } : SEM_SESSAO });
    const { container } = renderizarApp(caminho);
    await screen.findByRole('heading', { level: 1 });

    expect(await violacoesDeAcessibilidade(container)).toEqual([]);
  });
});
