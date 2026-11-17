import { fireEvent, screen, waitFor, within } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';

import { violacoesDeAcessibilidade } from '../../testes/acessibilidade';
import { ANA, FAVORITAS_VAZIAS, simularApi } from '../../testes/api';
import { renderizarApp } from '../../testes/renderizar';

/** API simulada com estado: apagar esvazia o histórico. */
function simular() {
  let apagado = false;
  return simularApi({
    'GET /api/eu': { corpo: ANA },
    ...FAVORITAS_VAZIAS,
    'GET /api/eu/historico': () => ({
      corpo: apagado
        ? []
        : [
            {
              disciplina_id: 4,
              disciplina_nome: 'Estruturas de Dados',
              mensagens: 6,
              ultima_em: '2026-11-16T20:00:00-03:00',
            },
          ],
    }),
    'DELETE /api/eu/historico': () => {
      apagado = true;
      return { status: 204 };
    },
  });
}

describe('meus dados (ACE-T52)', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('a aluna chega pelo cabeçalho e vê as conversas guardadas', async () => {
    simular();
    const { container } = renderizarApp('/');

    fireEvent.click(await screen.findByRole('link', { name: 'Meus dados' }));

    const lista = await screen.findByRole('list', { name: 'Conversas guardadas' });
    expect(within(lista).getByText('Estruturas de Dados')).toBeInTheDocument();
    expect(within(lista).getByText(/6 mensagens/)).toBeInTheDocument();
    expect(await violacoesDeAcessibilidade(container)).toEqual([]);
  });

  it('apagar o histórico pede confirmação e depois esvazia a lista', async () => {
    const { chamadas } = simular();
    renderizarApp('/meus-dados');

    fireEvent.click(await screen.findByRole('button', { name: 'Apagar meu histórico' }));
    expect(chamadas.some((c) => c.metodo === 'DELETE')).toBe(false);
    fireEvent.click(screen.getByRole('button', { name: 'Sim, apagar meu histórico' }));

    expect(await screen.findByText('Histórico apagado.')).toBeInTheDocument();
    await waitFor(() =>
      expect(screen.getByText('Você não tem conversas guardadas com o tutor.')).toBeInTheDocument(),
    );
  });

  it('cancelar não apaga nada', async () => {
    const { chamadas } = simular();
    renderizarApp('/meus-dados');

    fireEvent.click(await screen.findByRole('button', { name: 'Apagar meu histórico' }));
    fireEvent.click(screen.getByRole('button', { name: 'Cancelar' }));

    expect(screen.getByRole('button', { name: 'Apagar meu histórico' })).toBeInTheDocument();
    expect(chamadas.some((c) => c.metodo === 'DELETE')).toBe(false);
  });
});
