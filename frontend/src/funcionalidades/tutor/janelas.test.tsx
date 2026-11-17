import { fireEvent, screen, waitFor, within } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';

import { violacoesDeAcessibilidade } from '../../testes/acessibilidade';
import { CARLOS, DISCIPLINAS, simularApi } from '../../testes/api';
import { renderizarApp } from '../../testes/renderizar';

const ESTRUTURAS = DISCIPLINAS.find((d) => d.nome === 'Estruturas de Dados')!;
const URL_DAS_JANELAS = `/api/disciplinas/${ESTRUTURAS.id}/janelas-prova`;
const PAGINA = `/disciplinas/${ESTRUTURAS.id}/tutor/configuracao`;

/** Hora local: a tela mostra e lê os horários no fuso do navegador. */
const QUINTA_19H = new Date(2099, 10, 19, 19, 0);
const QUINTA_22H = new Date(2099, 10, 19, 22, 0);

type Janela = { id: number; inicio: string; fim: string | null };

/** API simulada com estado: criar e apagar mudam o que a lista devolve. */
function simular(inicio: Janela[] = [], respostaAoCriar?: { status: number; corpo: unknown }) {
  let janelas = [...inicio];
  let proximo = 100;
  const rotas: Parameters<typeof simularApi>[0] = {
    'GET /api/eu': { corpo: CARLOS },
    'GET /api/disciplinas': { corpo: DISCIPLINAS },
    [`GET /api/disciplinas/${ESTRUTURAS.id}/tutor/configuracao`]: {
      corpo: { modo_pistas: true, limite_diario: 40, politica: '' },
    },
    [`GET ${URL_DAS_JANELAS}`]: () => ({ corpo: janelas }),
    [`POST ${URL_DAS_JANELAS}`]: (chamada) => {
      if (respostaAoCriar) return respostaAoCriar;
      const dados = chamada.corpo as { inicio?: string; fim?: string };
      const nova = {
        id: proximo++,
        inicio: dados.inicio ?? new Date(Date.now() - 1000).toISOString(),
        fim: dados.fim ?? null,
      };
      janelas = [...janelas, nova];
      return { status: 201, corpo: nova };
    },
  };
  for (const id of [1, 2, 100, 101]) {
    rotas[`DELETE ${URL_DAS_JANELAS}/${id}`] = () => {
      janelas = janelas.filter((j) => j.id !== id);
      return { status: 204 };
    };
  }
  return simularApi(rotas);
}

describe('janelas de prova no painel do professor (TUT-T52)', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('pausa o tutor na hora e depois desliga o modo prova', async () => {
    const { chamadas } = simular();
    renderizarApp(PAGINA);

    fireEvent.click(await screen.findByRole('button', { name: 'Pausar o tutor agora' }));

    expect(await screen.findByText('O tutor está pausado agora.')).toBeInTheDocument();
    expect(chamadas.find((c) => c.metodo === 'POST')?.corpo).toEqual({});
    fireEvent.click(screen.getByRole('button', { name: 'Desligar o modo prova' }));
    expect(await screen.findByText('O tutor está respondendo normalmente.')).toBeInTheDocument();
    expect(chamadas.some((c) => c.metodo === 'DELETE')).toBe(true);
  });

  it('agenda uma janela de quinta, das 19h às 22h', async () => {
    const { chamadas } = simular();
    renderizarApp(PAGINA);

    fireEvent.change(await screen.findByLabelText('Dia da prova'), {
      target: { value: '2099-11-19' },
    });
    fireEvent.change(screen.getByLabelText('Começa às'), { target: { value: '19:00' } });
    fireEvent.change(screen.getByLabelText('Termina às'), { target: { value: '22:00' } });
    fireEvent.click(screen.getByRole('button', { name: 'Agendar janela de prova' }));

    const agendadas = await screen.findByRole('list', { name: 'Janelas de prova agendadas' });
    expect(await within(agendadas).findByText(/19:00 às 22:00/)).toBeInTheDocument();
    expect(chamadas.find((c) => c.metodo === 'POST')?.corpo).toEqual({
      inicio: QUINTA_19H.toISOString(),
      fim: QUINTA_22H.toISOString(),
    });
  });

  it('mostra o motivo quando a API recusa a janela', async () => {
    simular([], { status: 400, corpo: { fim: ['O fim precisa ser depois do início.'] } });
    renderizarApp(PAGINA);

    fireEvent.change(await screen.findByLabelText('Dia da prova'), {
      target: { value: '2099-11-19' },
    });
    fireEvent.change(screen.getByLabelText('Começa às'), { target: { value: '22:00' } });
    fireEvent.change(screen.getByLabelText('Termina às'), { target: { value: '19:00' } });
    fireEvent.click(screen.getByRole('button', { name: 'Agendar janela de prova' }));

    expect(await screen.findByRole('alert')).toHaveTextContent(
      'O fim precisa ser depois do início.',
    );
  });

  it('lista as janelas agendadas e apaga uma', async () => {
    simular([{ id: 2, inicio: QUINTA_19H.toISOString(), fim: QUINTA_22H.toISOString() }]);
    const { container } = renderizarApp(PAGINA);

    const agendadas = await screen.findByRole('list', { name: 'Janelas de prova agendadas' });
    expect(within(agendadas).getByText(/19:00 às 22:00/)).toBeInTheDocument();
    expect(await violacoesDeAcessibilidade(container)).toEqual([]);

    fireEvent.click(within(agendadas).getByRole('button', { name: /Apagar a janela/ }));

    await waitFor(() =>
      expect(screen.queryByRole('list', { name: 'Janelas de prova agendadas' })).toBeNull(),
    );
    expect(screen.getByText('Nenhuma prova agendada.')).toBeInTheDocument();
  });
});
