import { fireEvent, screen, waitFor, within } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';

import { violacoesDeAcessibilidade } from '../../testes/acessibilidade';
import { CARLOS, DISCIPLINAS, FAVORITAS_VAZIAS, simularApi } from '../../testes/api';
import { renderizarApp } from '../../testes/renderizar';

const PRONTA = {
  id: 1,
  tipo: 'material_pronto',
  texto: 'Aula 5, Pilhas, está pronta para o tutor.',
  link: '/disciplinas/4/materiais',
  lida: false,
  criada_em: '2026-11-17T10:00:00-03:00',
};
const ANTIGA = { ...PRONTA, id: 2, texto: 'Aula 4, Listas, está pronta para o tutor.', lida: true };

/** API simulada com estado: marcar como lida muda a contagem. */
function simular() {
  const lidas = new Set<number>();
  const lista = () => {
    const notificacoes = [PRONTA, ANTIGA].map((n) => ({ ...n, lida: n.lida || lidas.has(n.id) }));
    return { notificacoes, nao_lidas: notificacoes.filter((n) => !n.lida).length };
  };
  return simularApi({
    'GET /api/eu': { corpo: CARLOS },
    ...FAVORITAS_VAZIAS,
    'GET /api/disciplinas': { corpo: DISCIPLINAS },
    'GET /api/disciplinas/4/materiais': { corpo: [] },
    'GET /api/notificacoes': () => ({ corpo: lista() }),
    'POST /api/notificacoes/1/lida': () => {
      lidas.add(1);
      return { status: 204 };
    },
  });
}

describe('sino de notificações (MAT-T25)', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('mostra quantas notificações não foram lidas e abre a lista', async () => {
    simular();
    const { container } = renderizarApp('/');

    const sino = await screen.findByRole('button', { name: 'Notificações: 1 não lida' });
    expect(sino).toHaveAttribute('aria-expanded', 'false');
    fireEvent.click(sino);

    const lista = screen.getByRole('list', { name: 'Notificações' });
    expect(within(lista).getAllByRole('listitem')).toHaveLength(2);
    expect(within(lista).getByText('Aula 5, Pilhas, está pronta para o tutor.')).toBeVisible();
    expect(await violacoesDeAcessibilidade(container)).toEqual([]);
  });

  it('marca a notificação como lida e a contagem cai', async () => {
    const { chamadas } = simular();
    renderizarApp('/');

    fireEvent.click(await screen.findByRole('button', { name: 'Notificações: 1 não lida' }));
    fireEvent.click(
      screen.getByRole('button', {
        name: 'Marcar como lida: Aula 5, Pilhas, está pronta para o tutor.',
      }),
    );

    expect(await screen.findByRole('button', { name: 'Notificações' })).toBeInTheDocument();
    expect(
      chamadas.some((c) => c.metodo === 'POST' && c.caminho === '/api/notificacoes/1/lida'),
    ).toBe(true);
  });

  it('abrir a notificação leva à tela dela e a marca como lida', async () => {
    const { chamadas } = simular();
    const { roteador } = renderizarApp('/');

    fireEvent.click(await screen.findByRole('button', { name: 'Notificações: 1 não lida' }));
    fireEvent.click(
      screen.getByRole('link', { name: 'Aula 5, Pilhas, está pronta para o tutor.' }),
    );

    await waitFor(() => expect(roteador.state.location.pathname).toBe('/disciplinas/4/materiais'));
    expect(chamadas.some((c) => c.caminho === '/api/notificacoes/1/lida')).toBe(true);
  });
});
