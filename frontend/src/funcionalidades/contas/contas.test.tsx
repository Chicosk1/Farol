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
    expect(await screen.findByRole('heading', { level: 1, name: 'Olá, Ana' })).toBeInTheDocument();
    expect(chamadas.find((c) => c.metodo === 'POST')?.corpo).toEqual({ email: ANA.email });
  });

  it('entrar como professor usa o e-mail do Carlos', async () => {
    const { chamadas } = simularApi({
      'GET /api/eu': SEM_SESSAO,
      'POST /api/dev/entrar': { corpo: CARLOS },
    });
    renderizarApp('/entrar');

    fireEvent.click(await screen.findByRole('button', { name: 'Entrar como professor' }));

    expect(
      await screen.findByRole('heading', { level: 1, name: 'Olá, Carlos' }),
    ).toBeInTheDocument();
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

    expect(await screen.findByRole('heading', { level: 1, name: 'Olá, Ana' })).toBeInTheDocument();
    expect(screen.getByText(/feira|sábado|domingo/)).toBeInTheDocument();
  });

  it('sair encerra a sessão e volta para a tela de entrada', async () => {
    const { chamadas } = simularApi({
      'GET /api/eu': { corpo: ANA },
      ...FAVORITAS_VAZIAS,
      'POST /api/sair': { status: 204 },
    });
    const { roteador } = renderizarApp('/');

    fireEvent.click(await screen.findByRole('button', { name: 'Conta de Ana Souza' }));
    fireEvent.click(screen.getByRole('button', { name: 'Sair' }));

    await waitFor(() => expect(roteador.state.location.pathname).toBe('/entrar'));
    expect(chamadas.some((c) => c.metodo === 'POST' && c.caminho === '/api/sair')).toBe(true);
  });

  it.each(['/entrar', '/', '/entrar?erro=conta_externa'])(
    'não tem violações de acessibilidade em %s',
    async (caminho) => {
      simularApi({ 'GET /api/eu': caminho === '/' ? { corpo: ANA } : SEM_SESSAO });
      const { container } = renderizarApp(caminho);
      await screen.findByRole('heading', { level: 1 });

      expect(await violacoesDeAcessibilidade(container)).toEqual([]);
    },
  );
});

describe('login com o Google e troca de perfil (ACE-T23)', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
    document.cookie = 'csrftoken=; expires=Thu, 01 Jan 1970 00:00:00 GMT';
  });

  it('o botão do Google envia o formulário ao allauth com o token CSRF (ACE-RF-01)', async () => {
    document.cookie = 'csrftoken=token-do-teste';
    simularApi({ 'GET /api/eu': SEM_SESSAO });
    renderizarApp('/entrar');

    const botao = await screen.findByRole('button', { name: 'Entrar com o Google' });
    const formulario = botao.closest('form');
    expect(formulario).toHaveAttribute('method', 'post');
    expect(formulario).toHaveAttribute('action', '/contas/google/login/');
    expect(formulario?.querySelector('input[name="csrfmiddlewaretoken"]')).toHaveValue(
      'token-do-teste',
    );
  });

  it('sem o Google configurado, explica e não mostra o botão', async () => {
    simularApi({
      'GET /api/eu': SEM_SESSAO,
      'GET /api/entrada': { corpo: { google: false, desenvolvimento: true } },
    });
    renderizarApp('/entrar');

    expect(
      await screen.findByText('O login com o Google ainda não foi configurado neste ambiente.'),
    ).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: 'Entrar com o Google' })).not.toBeInTheDocument();
  });

  it.each([
    ['conta_externa', 'Use a sua conta institucional.'],
    ['conta_desativada', 'A sua conta está desativada no Farol.'],
    ['falha', 'Não foi possível entrar com o Google.'],
  ])('a volta do Google com erro %s mostra o aviso', async (erro, mensagem) => {
    simularApi({ 'GET /api/eu': SEM_SESSAO });
    renderizarApp(`/entrar?erro=${erro}`);

    expect(await screen.findByRole('alert')).toHaveTextContent(mensagem);
  });

  it('quem tem dois perfis troca o perfil em uso sem sair (ACE-RF-03)', async () => {
    const duplo = { ...CARLOS, perfis: ['professor', 'aluno'], perfil_ativo: 'professor' };
    const { chamadas } = simularApi({
      'GET /api/eu': { corpo: duplo },
      ...FAVORITAS_VAZIAS,
      'POST /api/eu/perfil-ativo': { corpo: { ...duplo, perfil_ativo: 'aluno' } },
    });
    renderizarApp('/');

    fireEvent.click(await screen.findByRole('button', { name: 'Conta de Carlos Mendes' }));
    const seletor = screen.getByRole('combobox', { name: 'Perfil em uso' });
    expect(seletor).toHaveValue('professor');
    fireEvent.change(seletor, { target: { value: 'aluno' } });

    await waitFor(() =>
      expect(screen.getByRole('link', { name: 'Farol, página inicial' })).toHaveTextContent(
        'Tutor de estudos',
      ),
    );
    expect(chamadas.find((c) => c.caminho === '/api/eu/perfil-ativo')?.corpo).toEqual({
      perfil: 'aluno',
    });
  });

  it('quem tem um perfil só não vê a troca de perfil', async () => {
    simularApi({ 'GET /api/eu': { corpo: ANA }, ...FAVORITAS_VAZIAS });
    renderizarApp('/');

    await screen.findByRole('heading', { name: 'Olá, Ana' });
    fireEvent.click(screen.getByRole('button', { name: 'Conta de Ana Souza' }));
    expect(screen.queryByRole('combobox', { name: 'Perfil em uso' })).not.toBeInTheDocument();
  });

  it('não tem violações de acessibilidade com a troca de perfil', async () => {
    const duplo = { ...CARLOS, perfis: ['professor', 'aluno'], perfil_ativo: 'professor' };
    simularApi({ 'GET /api/eu': { corpo: duplo }, ...FAVORITAS_VAZIAS });
    const { container } = renderizarApp('/');
    fireEvent.click(await screen.findByRole('button', { name: 'Conta de Carlos Mendes' }));
    await screen.findByRole('combobox', { name: 'Perfil em uso' });

    expect(await violacoesDeAcessibilidade(container)).toEqual([]);
  });
});
