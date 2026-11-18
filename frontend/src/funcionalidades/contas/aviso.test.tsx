import { fireEvent, screen, waitFor, within } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';

import { violacoesDeAcessibilidade } from '../../testes/acessibilidade';
import { ANA, ANA_NOVA, AVISO, FAVORITAS_VAZIAS, simularApi } from '../../testes/api';
import { renderizarApp } from '../../testes/renderizar';

describe('aviso de privacidade (ACE-T53)', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('na primeira entrada, mostra o aviso com o que é registrado, para quê e por quanto tempo', async () => {
    simularApi({
      'GET /api/eu': { corpo: ANA_NOVA },
      'GET /api/aviso-privacidade': { corpo: AVISO },
      ...FAVORITAS_VAZIAS,
    });
    renderizarApp('/');

    const aviso = await screen.findByRole('dialog', { name: AVISO.titulo });
    expect(aviso).toHaveAttribute('aria-modal', 'true');
    for (const item of AVISO.itens) {
      expect(within(aviso).getByRole('heading', { name: item.titulo })).toBeInTheDocument();
      expect(within(aviso).getByText(item.texto)).toBeInTheDocument();
    }
    expect(within(aviso).getByRole('button', { name: 'Entendi' })).toBeInTheDocument();
  });

  it('o resto da página fica bloqueado até o aluno confirmar', async () => {
    simularApi({
      'GET /api/eu': { corpo: ANA_NOVA },
      'GET /api/aviso-privacidade': { corpo: AVISO },
      ...FAVORITAS_VAZIAS,
    });
    renderizarApp('/');
    await screen.findByRole('dialog');

    const principal = document.querySelector('main');
    expect(principal?.closest('[inert]')).not.toBeNull();
    expect(screen.getByRole('dialog').closest('[inert]')).toBeNull();
  });

  it('o foco vai para o aviso quando ele abre', async () => {
    simularApi({
      'GET /api/eu': { corpo: ANA_NOVA },
      'GET /api/aviso-privacidade': { corpo: AVISO },
      ...FAVORITAS_VAZIAS,
    });
    renderizarApp('/');

    const aviso = await screen.findByRole('dialog');

    await waitFor(() => expect(aviso.contains(document.activeElement)).toBe(true));
  });

  it('confirmar envia a versão lida, fecha o aviso e libera a página', async () => {
    const { chamadas } = simularApi({
      'GET /api/eu': { corpo: ANA_NOVA },
      'GET /api/aviso-privacidade': { corpo: AVISO },
      'POST /api/eu/ciencia-privacidade': { status: 204 },
      ...FAVORITAS_VAZIAS,
    });
    renderizarApp('/');

    fireEvent.click(await screen.findByRole('button', { name: 'Entendi' }));

    await waitFor(() => expect(screen.queryByRole('dialog')).not.toBeInTheDocument());
    expect(chamadas.find((c) => c.metodo === 'POST')?.corpo).toEqual({ versao: '1' });
    expect(document.querySelector('[inert]')).toBeNull();
  });

  it('a tecla Esc não fecha o aviso: é preciso confirmar', async () => {
    simularApi({
      'GET /api/eu': { corpo: ANA_NOVA },
      'GET /api/aviso-privacidade': { corpo: AVISO },
      ...FAVORITAS_VAZIAS,
    });
    renderizarApp('/');
    const aviso = await screen.findByRole('dialog');

    fireEvent.keyDown(aviso, { key: 'Escape' });

    expect(screen.getByRole('dialog')).toBeInTheDocument();
  });

  it('se a confirmação falhar, avisa e mantém o aviso na tela', async () => {
    simularApi({
      'GET /api/eu': { corpo: ANA_NOVA },
      'GET /api/aviso-privacidade': { corpo: AVISO },
      'POST /api/eu/ciencia-privacidade': { status: 500 },
      ...FAVORITAS_VAZIAS,
    });
    renderizarApp('/');

    fireEvent.click(await screen.findByRole('button', { name: 'Entendi' }));

    expect(await screen.findByRole('alert')).toHaveTextContent(
      'Não foi possível registrar a sua confirmação.',
    );
    expect(screen.getByRole('dialog')).toBeInTheDocument();
  });

  it('quem já leu a versão atual não vê o aviso', async () => {
    simularApi({ 'GET /api/eu': { corpo: ANA }, ...FAVORITAS_VAZIAS });
    renderizarApp('/');

    await screen.findByRole('heading', { level: 1, name: /^Olá, / });
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
  });

  it('não tem violações de acessibilidade com o aviso aberto', async () => {
    simularApi({
      'GET /api/eu': { corpo: ANA_NOVA },
      'GET /api/aviso-privacidade': { corpo: AVISO },
      ...FAVORITAS_VAZIAS,
    });
    const { container } = renderizarApp('/');
    await screen.findByRole('dialog');

    expect(await violacoesDeAcessibilidade(container)).toEqual([]);
  });
});
