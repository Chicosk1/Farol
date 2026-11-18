import { fireEvent, screen } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';

import { violacoesDeAcessibilidade } from '../../testes/acessibilidade';
import { CARLOS, DISCIPLINAS, ESTRUTURAS, simularApi } from '../../testes/api';
import { renderizarApp } from '../../testes/renderizar';

const ID = ESTRUTURAS.id;
const RADAR = {
  semana: '2026-11-16',
  rotulo: 'Semana de 16/11 a 22/11',
  indicadores: {
    alunos_ativos: 31,
    matriculados: 46,
    perguntas: 120,
    acerto_medio: 64,
    duvidas_sem_resposta: 3,
  },
  pouco_uso: false,
  topicos: [
    { nome: 'Aula 5 · Árvores AVL', alunos: 14, exemplos: ['Como balanceia?'], material: 15 },
  ],
  acertos: [{ topico: 'Rotações', taxa: 42, alunos: 20, material: 15 }],
  questoes_com_menor_acerto: [],
  sugestao: [{ nome: 'Aula 5 · Árvores AVL', material: 15 }],
};

function simular(radar: object = RADAR) {
  return simularApi({
    'GET /api/eu': { corpo: CARLOS },
    'GET /api/disciplinas': { corpo: DISCIPLINAS },
    [`GET /api/disciplinas/${ID}`]: { corpo: ESTRUTURAS },
    [`GET /api/disciplinas/${ID}/radar`]: { corpo: radar },
    [`GET /api/disciplinas/${ID}/radar/semanas`]: {
      corpo: [{ semana: '2026-11-16', rotulo: 'Semana de 16/11 a 22/11', atual: true }],
    },
    [`POST /api/disciplinas/${ID}/radar/exemplos-ocultos`]: { status: 204 },
  });
}

describe('radar da turma (RAD-T40, RAD-T31)', () => {
  afterEach(() => vi.unstubAllGlobals());

  it('mostra os indicadores, a sugestão, os tópicos e o acerto', async () => {
    simular();
    const { container } = renderizarApp(`/disciplinas/${ID}/radar`);

    expect(await screen.findByText('Perguntas ao tutor')).toBeInTheDocument();
    expect(screen.getByText('120')).toBeInTheDocument();
    expect(screen.getByText('64%')).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Gerar 5 questões de revisão' })).toHaveAttribute(
      'href',
      `/disciplinas/${ID}/questoes?aula=15&quantidade=5`,
    );
    expect(screen.getByText('42%')).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Radar da turma' })).toBeInTheDocument();
    expect(await violacoesDeAcessibilidade(container)).toEqual([]);
  });

  it('tocar no tópico mostra os exemplos, que o professor pode ocultar', async () => {
    const { chamadas } = simular();
    renderizarApp(`/disciplinas/${ID}/radar`);

    fireEvent.click(await screen.findByRole('button', { name: /Aula 5 · Árvores AVL/ }));
    fireEvent.click(screen.getByRole('button', { name: 'Ocultar o exemplo: Como balanceia?' }));

    await vi.waitFor(() =>
      expect(chamadas.find((c) => c.metodo === 'POST')?.corpo).toEqual({
        texto: 'Como balanceia?',
      }),
    );
  });

  it('com pouco uso, mostra só os indicadores', async () => {
    simular({ ...RADAR, pouco_uso: true, topicos: [], acertos: [], sugestao: [] });
    renderizarApp(`/disciplinas/${ID}/radar`);

    expect(await screen.findByText(/Menos de 5 alunos usaram o Farol/)).toBeInTheDocument();
    expect(screen.queryByText('Tópicos com mais dúvidas')).not.toBeInTheDocument();
  });
});
