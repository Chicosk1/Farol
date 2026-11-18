import { fireEvent, screen, waitFor, within } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';

import { violacoesDeAcessibilidade } from '../../testes/acessibilidade';
import { ANA, CARLOS, DISCIPLINAS, ESTRUTURAS, simularApi } from '../../testes/api';
import { renderizarApp } from '../../testes/renderizar';

const ID = ESTRUTURAS.id;
const MATERIAL = { id: 10, aula_numero: 3, aula_titulo: 'Pilhas e filas', status: 'pronto' };

function questao(id: number, campos: Record<string, unknown> = {}) {
  return {
    id,
    material: MATERIAL.id,
    aula_numero: 3,
    aula_titulo: 'Pilhas e filas',
    enunciado: `Qual regra a pilha segue? (${id})`,
    alternativas: ['LIFO', 'FIFO', 'Por prioridade', 'Aleatória'],
    correta: 0,
    justificativa: 'Na pilha, o último a entrar é o primeiro a sair.',
    topico: 'Pilhas',
    trecho: { id: 7, pagina: 2 },
    status: 'pendente',
    nova: true,
    editada: false,
    origem_retirada: false,
    ...campos,
  };
}

/** API do professor com estado: aprovar move a questão para publicadas. */
function simularProfessor() {
  const questoes = [questao(1), questao(2, { nova: false })];
  const contar = (s: string) => questoes.filter((q) => q.status === s).length;
  const lista = (status: string) => () => ({
    corpo: {
      contagens: {
        pendente: contar('pendente'),
        publicada: contar('publicada'),
        descartada: contar('descartada'),
      },
      questoes: questoes.filter((q) => q.status === status),
    },
  });
  const rotas: Parameters<typeof simularApi>[0] = {
    'GET /api/eu': { corpo: CARLOS },
    'GET /api/disciplinas': { corpo: DISCIPLINAS },
    [`GET /api/disciplinas/${ID}`]: { corpo: ESTRUTURAS },
    [`GET /api/disciplinas/${ID}/materiais`]: { corpo: [MATERIAL] },
    [`GET /api/disciplinas/${ID}/questoes?status=pendente`]: lista('pendente'),
    [`GET /api/disciplinas/${ID}/questoes?status=publicada`]: lista('publicada'),
    [`GET /api/disciplinas/${ID}/questoes?status=descartada`]: lista('descartada'),
    [`POST /api/materiais/${MATERIAL.id}/geracoes`]: () => {
      questoes.unshift(questao(3, { enunciado: 'Rascunho novo da fila?' }));
      return {
        status: 202,
        corpo: { id: 1, material: MATERIAL.id, quantidade: 5, status: 'pronto', geradas: 1 },
      };
    },
  };
  for (const q of questoes.concat(questao(3))) {
    rotas[`PATCH /api/questoes/${q.id}`] = (chamada) => {
      const alvo = questoes.find((x) => x.id === q.id)!;
      Object.assign(alvo, chamada.corpo, { nova: false });
      return { corpo: alvo };
    };
  }
  return simularApi(rotas);
}

describe('questões do professor (QUE-T23, QUE-T32)', () => {
  afterEach(() => vi.unstubAllGlobals());

  it('mostra os rascunhos pendentes com o gabarito, as contagens e o trecho', async () => {
    simularProfessor();
    const { container } = renderizarApp(`/disciplinas/${ID}/questoes`);

    const cartao = await screen.findByRole('article', { name: 'Qual regra a pilha segue? (1)' });
    expect(within(cartao).getByText('Novo rascunho')).toBeInTheDocument();
    expect(within(cartao).getByText('Correta')).toBeInTheDocument();
    expect(within(cartao).getByRole('link', { name: 'Aula 3, p. 2' })).toHaveAttribute(
      'href',
      '/trechos/7',
    );
    expect(screen.getByRole('tab', { name: 'Pendentes (2)' })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Questões' })).toBeInTheDocument();
    expect(await violacoesDeAcessibilidade(container)).toEqual([]);
  });

  it('aprovar publica a questão e atualiza as contagens', async () => {
    const { chamadas } = simularProfessor();
    renderizarApp(`/disciplinas/${ID}/questoes`);

    fireEvent.click(
      await screen.findByRole('button', { name: 'Aprovar: Qual regra a pilha segue? (1)' }),
    );

    expect(await screen.findByRole('tab', { name: 'Publicadas (1)' })).toBeInTheDocument();
    expect(chamadas.find((c) => c.metodo === 'PATCH')?.corpo).toEqual({ status: 'publicada' });
    expect(screen.getByText('Questão publicada no quiz da turma.')).toBeInTheDocument();
  });

  it('editar envia o enunciado e o gabarito novos', async () => {
    const { chamadas } = simularProfessor();
    renderizarApp(`/disciplinas/${ID}/questoes`);

    fireEvent.click(
      await screen.findByRole('button', { name: 'Editar: Qual regra a pilha segue? (1)' }),
    );
    fireEvent.change(screen.getByLabelText('Enunciado'), {
      target: { value: 'Que ordem a pilha segue?' },
    });
    fireEvent.click(screen.getByLabelText('Alternativa B é a correta'));
    fireEvent.click(screen.getByRole('button', { name: 'Salvar' }));

    await waitFor(() => expect(chamadas.some((c) => c.metodo === 'PATCH')).toBe(true));
    const corpo = chamadas.find((c) => c.metodo === 'PATCH')!.corpo as Record<string, unknown>;
    expect(corpo.enunciado).toBe('Que ordem a pilha segue?');
    expect(corpo.correta).toBe(1);
  });

  it('gerar rascunhos pede a quantidade escolhida e mostra os novos', async () => {
    const { chamadas } = simularProfessor();
    renderizarApp(`/disciplinas/${ID}/questoes`);

    await screen.findByRole('option', { name: 'Aula 3 · Pilhas e filas' });
    fireEvent.change(screen.getByLabelText('Quantidade'), { target: { value: '10' } });
    fireEvent.click(screen.getByRole('button', { name: 'Gerar rascunhos' }));

    expect(
      await screen.findByRole('article', { name: 'Rascunho novo da fila?' }),
    ).toBeInTheDocument();
    expect(chamadas.find((c) => c.metodo === 'POST')?.corpo).toEqual({ quantidade: 10 });
    expect(screen.getByText('1 rascunho gerado. Revise antes de publicar.')).toBeInTheDocument();
  });
});

const QUIZ = {
  material: MATERIAL.id,
  disciplina: ID,
  aula_numero: 3,
  aula_titulo: 'Pilhas e filas',
  pausado: false,
  questoes: [
    {
      id: 1,
      enunciado: 'Qual regra a pilha segue?',
      alternativas: ['LIFO', 'FIFO', 'X', 'Y'],
      topico: 'Pilhas',
    },
    {
      id: 2,
      enunciado: 'Qual regra a fila segue?',
      alternativas: ['LIFO', 'FIFO', 'X', 'Y'],
      topico: 'Filas',
    },
  ],
  respostas: [],
  concluido: false,
};

function retorno(questao: number, alternativa: number, correta: number, topico: string) {
  return {
    questao,
    alternativa,
    acerto: alternativa === correta,
    correta,
    justificativa: 'Explicação do material.',
    topico,
    trecho: { id: 7, rotulo: 'Aula 3, p. 2' },
  };
}

function simularAluna(quiz: object = QUIZ) {
  return simularApi({
    'GET /api/eu': { corpo: ANA },
    [`GET /api/disciplinas/${ID}`]: { corpo: ESTRUTURAS },
    [`GET /api/materiais/${MATERIAL.id}/quiz`]: { corpo: quiz },
    'POST /api/questoes/1/respostas': (c) => ({
      corpo: retorno(1, (c.corpo as { alternativa: number }).alternativa, 0, 'Pilhas'),
    }),
    'POST /api/questoes/2/respostas': (c) => ({
      corpo: retorno(2, (c.corpo as { alternativa: number }).alternativa, 1, 'Filas'),
    }),
  });
}

describe('quiz da aula para o aluno (QUE-T42)', () => {
  afterEach(() => vi.unstubAllGlobals());

  it('errar mostra a correta, a justificativa, o trecho e o atalho para o tutor', async () => {
    simularAluna();
    const { container } = renderizarApp(`/disciplinas/${ID}/quiz/${MATERIAL.id}`);

    expect(await screen.findByText('Questão 1 de 2 · Pilhas')).toBeInTheDocument();
    expect(await violacoesDeAcessibilidade(container)).toEqual([]);
    fireEvent.click(screen.getByRole('button', { name: 'B: FIFO' }));

    expect(await screen.findByText(/Não foi dessa vez/)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'A: LIFO, resposta correta' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'B: FIFO, sua resposta' })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Ver Aula 3, p. 2' })).toHaveAttribute(
      'href',
      '/trechos/7',
    );
    const tutor = screen.getByRole('link', { name: 'Perguntar ao tutor sobre isso' });
    expect(tutor.getAttribute('href')).toMatch(new RegExp(`^/disciplinas/${ID}/tutor\\?pergunta=`));
    expect(await violacoesDeAcessibilidade(container)).toEqual([]);
  });

  it('no fim mostra os acertos e os tópicos para revisar com o tutor', async () => {
    simularAluna();
    renderizarApp(`/disciplinas/${ID}/quiz/${MATERIAL.id}`);

    fireEvent.click(await screen.findByRole('button', { name: 'A: LIFO' }));
    fireEvent.click(await screen.findByRole('button', { name: 'Próxima' }));
    fireEvent.click(await screen.findByRole('button', { name: 'A: LIFO' }));
    fireEvent.click(await screen.findByRole('button', { name: 'Ver resultado' }));

    expect(await screen.findByRole('heading', { name: 'Quiz concluído' })).toBeInTheDocument();
    expect(screen.getByText('1 de 2')).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Filas' })).toBeInTheDocument();
  });

  it('volta da questão em que parou', async () => {
    simularAluna({ ...QUIZ, respostas: [retorno(1, 0, 0, 'Pilhas')] });
    renderizarApp(`/disciplinas/${ID}/quiz/${MATERIAL.id}`);

    expect(await screen.findByText('Questão 2 de 2 · Filas')).toBeInTheDocument();
  });

  it('no modo prova, o quiz aparece pausado', async () => {
    simularAluna({ ...QUIZ, pausado: true, questoes: [] });
    renderizarApp(`/disciplinas/${ID}/quiz/${MATERIAL.id}`);

    expect(await screen.findByText('O quiz está pausado durante a prova')).toBeInTheDocument();
  });

  it('a página da disciplina lista os quizzes com o andamento', async () => {
    simularApi({
      'GET /api/eu': { corpo: ANA },
      [`GET /api/disciplinas/${ID}`]: { corpo: ESTRUTURAS },
      [`GET /api/disciplinas/${ID}/materiais`]: { corpo: [] },
      [`GET /api/disciplinas/${ID}/quizzes`]: {
        corpo: [
          {
            material: 10,
            aula_numero: 3,
            aula_titulo: 'Pilhas e filas',
            questoes: 4,
            respondidas: 4,
            acertos: 3,
          },
        ],
      },
    });
    renderizarApp(`/disciplinas/${ID}`);

    const link = await screen.findByRole('link', { name: /Quiz da Aula 3/ });
    expect(link).toHaveAttribute('href', `/disciplinas/${ID}/quiz/10`);
    expect(link).toHaveTextContent('Concluído: 3 de 4 acertos');
  });
});
