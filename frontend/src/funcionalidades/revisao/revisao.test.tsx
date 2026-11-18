import { fireEvent, screen, waitFor } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';

import { violacoesDeAcessibilidade } from '../../testes/acessibilidade';
import { ANA, simularApi } from '../../testes/api';
import { renderizarApp } from '../../testes/renderizar';

const CARTOES = [
  {
    id: 11,
    disciplina: 4,
    disciplina_nome: 'Estruturas de Dados',
    enunciado: 'Qual regra a pilha segue?',
    alternativas: ['LIFO', 'FIFO', 'X', 'Y'],
    topico: 'Pilhas',
  },
  {
    id: 12,
    disciplina: 4,
    disciplina_nome: 'Estruturas de Dados',
    enunciado: 'Qual regra a fila segue?',
    alternativas: ['LIFO', 'FIFO', 'X', 'Y'],
    topico: 'Filas',
  },
];

function dias(feitas: boolean[]) {
  return feitas.map((feita, i) => ({ data: `2026-11-${String(12 + i).padStart(2, '0')}`, feita }));
}

function sessao(campos: Record<string, unknown> = {}) {
  return {
    data: '2026-11-18',
    cartoes: CARTOES,
    respostas: [],
    concluida: false,
    disciplinas: ['Estruturas de Dados'],
    minutos: 1,
    tem_questoes: true,
    sequencia: dias([true, true, false, true, true, true, false]),
    dias_seguidos: 3,
    ...campos,
  };
}

function retorno(cartao: number, alternativa: number, correta: number, topico: string) {
  return {
    cartao,
    questao: cartao,
    alternativa,
    acerto: alternativa === correta,
    correta,
    justificativa: 'Explicação do material.',
    topico,
    trecho: { id: 7, rotulo: 'Aula 3, p. 2' },
  };
}

describe('revisão do dia (REV-T23, REV-T24, REV-T40)', () => {
  afterEach(() => vi.unstubAllGlobals());

  it('a tela inicial mostra o cartão da revisão e a sequência', async () => {
    simularApi({ 'GET /api/eu': { corpo: ANA }, 'GET /api/revisao/hoje': { corpo: sessao() } });
    const { container } = renderizarApp('/');

    expect(
      await screen.findByText('2 cartões de Estruturas de Dados, cerca de 1 minuto.'),
    ).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Começar revisão' })).toHaveAttribute(
      'href',
      '/revisao',
    );
    expect(screen.getByRole('heading', { name: '3 dias seguidos' })).toBeInTheDocument();
    expect(
      screen.getByRole('img', { name: 'Revisão feita em 5 dos últimos 7 dias' }),
    ).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Revisão do dia' })).toBeInTheDocument();
    expect(await violacoesDeAcessibilidade(container)).toEqual([]);
  });

  it('responder e avaliar mostra o retorno e quando o cartão volta, até o resumo', async () => {
    const respostas: object[] = [];
    simularApi({
      'GET /api/eu': { corpo: ANA },
      'GET /api/revisao/hoje': () => ({ corpo: sessao({ respostas }) }),
      'POST /api/revisao/cartoes/11/resposta': () => {
        const r = retorno(11, 1, 0, 'Pilhas');
        respostas.push({ ...r, avaliacao: '', volta: '' });
        return { corpo: r };
      },
      'POST /api/revisao/cartoes/11/avaliacao': () => {
        Object.assign(respostas[0]!, { avaliacao: 'bom', volta: 'Este cartão volta amanhã.' });
        return { corpo: { proxima_data: '2026-11-19', texto: 'Este cartão volta amanhã.' } };
      },
      'POST /api/revisao/cartoes/12/resposta': () => {
        const r = retorno(12, 1, 1, 'Filas');
        respostas.push({ ...r, avaliacao: '', volta: '' });
        return { corpo: r };
      },
      'POST /api/revisao/cartoes/12/avaliacao': () => {
        Object.assign(respostas[1]!, { avaliacao: 'facil', volta: 'Este cartão volta em 4 dias.' });
        return { corpo: { proxima_data: '2026-11-22', texto: 'Este cartão volta em 4 dias.' } };
      },
    });
    const { container } = renderizarApp('/revisao');

    fireEvent.click(await screen.findByRole('button', { name: 'B: FIFO' }));
    expect(await screen.findByText(/Não foi dessa vez/)).toBeInTheDocument();
    expect(await violacoesDeAcessibilidade(container)).toEqual([]);
    fireEvent.click(screen.getByRole('button', { name: 'Bom' }));
    expect(await screen.findByText('Este cartão volta amanhã.')).toBeInTheDocument();

    fireEvent.click(await screen.findByRole('button', { name: 'B: FIFO' }));
    fireEvent.click(await screen.findByRole('button', { name: 'Fácil' }));

    expect(await screen.findByRole('heading', { name: 'Revisão concluída' })).toBeInTheDocument();
    expect(screen.getByText('1 de 2')).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Pilhas' })).toBeInTheDocument();
  });

  it('sem questões publicadas, explica que a revisão ainda não começou', async () => {
    simularApi({ 'GET /api/eu': { corpo: ANA } });
    renderizarApp('/revisao');

    expect(await screen.findByText('A revisão ainda não começou')).toBeInTheDocument();
  });

  it('o lembrete fica em Meus dados e pode ser ligado', async () => {
    const { chamadas } = simularApi({
      'GET /api/eu': { corpo: ANA },
      'GET /api/eu/historico': { corpo: [] },
      'PUT /api/eu/lembrete': (c) => ({ corpo: c.corpo }),
    });
    renderizarApp('/meus-dados');

    fireEvent.click(await screen.findByLabelText('Lembrete diário por e-mail'));
    fireEvent.change(screen.getByLabelText('Horário do lembrete'), { target: { value: '07:00' } });
    fireEvent.click(screen.getByRole('button', { name: 'Salvar lembrete' }));

    await waitFor(() =>
      expect(chamadas.find((c) => c.metodo === 'PUT')?.corpo).toEqual({
        ligado: true,
        horario: '07:00',
      }),
    );
  });
});
