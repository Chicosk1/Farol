import { fireEvent, screen, waitFor, within } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';

import type { EstadoDoTutor } from '../../api/cliente';
import { violacoesDeAcessibilidade } from '../../testes/acessibilidade';
import { ANA, DISCIPLINAS, simularApi, type RespostaSimulada } from '../../testes/api';
import { renderizarApp } from '../../testes/renderizar';

const ESTRUTURAS = DISCIPLINAS.find((d) => d.nome === 'Estruturas de Dados')!;
const URL_DO_TUTOR = `/api/disciplinas/${ESTRUTURAS.id}/tutor`;
const CITACAO = { ordem: 1, rotulo: 'Aula 4, p. 5', trecho_id: 31, material_id: 7, pagina: 5 };

function estado(mudancas: Partial<EstadoDoTutor> = {}): EstadoDoTutor {
  return {
    modo_pistas: true,
    politica: '',
    pausado: false,
    uso: { usadas: 3, limite: 40 },
    conversa_id: null,
    mensagens: [],
    sugestoes: [],
    ...mudancas,
  };
}

const CONVERSA_GUARDADA = estado({
  conversa_id: 9,
  mensagens: [
    { id: 1, autor: 'aluno', texto: 'O que é uma lista encadeada?', citacoes: [] },
    {
      id: 2,
      autor: 'tutor',
      tipo: 'resposta',
      texto: 'Uma lista encadeada é formada por nós com ponteiros. [1]',
      citacoes: [CITACAO],
    },
  ],
});

function simularTutor(
  tutor: EstadoDoTutor,
  pergunta?: RespostaSimulada,
  duvidas: { mensagem_id: number; status: string }[] = [],
) {
  return simularApi({
    'GET /api/eu': { corpo: ANA },
    'GET /api/disciplinas': { corpo: DISCIPLINAS },
    [`GET ${URL_DO_TUTOR}`]: { corpo: tutor },
    [`GET /api/disciplinas/${ESTRUTURAS.id}/minhas-duvidas`]: { corpo: duvidas },
    ...(pergunta ? { [`POST ${URL_DO_TUTOR}/perguntas`]: pergunta } : {}),
  });
}

const RESPOSTA_EM_EVENTOS: RespostaSimulada = {
  eventos: [
    ['inicio', { conversa_id: 9 }],
    ['texto', { texto: 'Uma pilha segue a ordem LIFO. [1] ' }],
    ['citacao', { ...CITACAO, rotulo: 'Aula 5, p. 3', pagina: 3 }],
    ['texto', { texto: 'O último a entrar é o primeiro a sair. [1]' }],
    ['fim', { tipo: 'resposta', mensagem_id: 12 }],
  ],
};

async function enviarPergunta(texto: string) {
  fireEvent.change(await screen.findByLabelText('Sua pergunta'), { target: { value: texto } });
  fireEvent.click(screen.getByRole('button', { name: 'Enviar pergunta' }));
}

describe('tela do tutor (TUT-T24)', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('mostra a conversa guardada, com a citação que abre o PDF na página citada', async () => {
    simularTutor(CONVERSA_GUARDADA);
    renderizarApp(`/disciplinas/${ESTRUTURAS.id}/tutor`);

    expect(
      await screen.findByRole('heading', { name: 'Tutor de Estruturas de Dados' }),
    ).toBeInTheDocument();
    const conversa = await screen.findByRole('list', { name: 'Conversa com o tutor' });
    expect(within(conversa).getByText('O que é uma lista encadeada?')).toBeInTheDocument();
    const citacao = within(conversa).getByRole('link', { name: /Aula 4, p\. 5/ });
    expect(citacao).toHaveAttribute('href', '/trechos/31');
    expect(screen.getByText('3 de 40 perguntas hoje')).toBeInTheDocument();
    expect(screen.getByText('Modo pistas ligado')).toBeInTheDocument();
  });

  it('não tem violações de acessibilidade', async () => {
    simularTutor(CONVERSA_GUARDADA);
    const { container } = renderizarApp(`/disciplinas/${ESTRUTURAS.id}/tutor`);

    await screen.findByRole('list', { name: 'Conversa com o tutor' });
    expect(await violacoesDeAcessibilidade(container)).toEqual([]);
  });

  it('envia a pergunta e mostra a resposta em streaming, com a citação e o uso atualizado', async () => {
    const { chamadas } = simularTutor(estado(), RESPOSTA_EM_EVENTOS);
    renderizarApp(`/disciplinas/${ESTRUTURAS.id}/tutor`);

    await enviarPergunta('O que é uma pilha?');

    const conversa = await screen.findByRole('list', { name: 'Conversa com o tutor' });
    expect(await within(conversa).findByText(/O último a entrar/)).toBeInTheDocument();
    expect(within(conversa).getByText('O que é uma pilha?')).toBeInTheDocument();
    expect(within(conversa).getByRole('link', { name: /Aula 5, p\. 3/ })).toHaveAttribute(
      'href',
      '/trechos/31',
    );
    expect(screen.getByText('4 de 40 perguntas hoje')).toBeInTheDocument();
    const pergunta = chamadas.find((c) => c.metodo === 'POST');
    expect(pergunta?.corpo).toEqual({ texto: 'O que é uma pilha?' });
    expect(screen.getByLabelText('Sua pergunta')).toHaveValue('');
  });

  it('anuncia a resposta nova para leitores de tela quando ela termina', async () => {
    simularTutor(estado(), RESPOSTA_EM_EVENTOS);
    renderizarApp(`/disciplinas/${ESTRUTURAS.id}/tutor`);

    await enviarPergunta('O que é uma pilha?');

    await waitFor(() =>
      expect(screen.getByTestId('anuncio-do-tutor')).toHaveTextContent(
        'O tutor respondeu: Uma pilha segue a ordem LIFO. [1] O último a entrar é o primeiro a sair. [1]',
      ),
    );
    expect(screen.getByTestId('anuncio-do-tutor')).toHaveAttribute('aria-live', 'polite');
  });

  it('marca a resposta em modo pistas', async () => {
    simularTutor(estado(), {
      eventos: [
        ['inicio', { conversa_id: 9 }],
        ['texto', { texto: 'Releia o trecho [1]: qual operação tira o elemento do topo?' }],
        ['citacao', CITACAO],
        ['fim', { tipo: 'pistas', mensagem_id: 12 }],
      ],
    });
    renderizarApp(`/disciplinas/${ESTRUTURAS.id}/tutor`);

    await enviarPergunta('Me dá a resposta do exercício de pilha');

    const conversa = await screen.findByRole('list', { name: 'Conversa com o tutor' });
    expect(await within(conversa).findByText('Modo pistas')).toBeInTheDocument();
  });

  it('com a conversa vazia, mostra as sugestões e envia a que o aluno escolher', async () => {
    const { chamadas } = simularTutor(
      estado({ sugestoes: ['Quais são as ideias principais da aula 5, Pilhas e filas?'] }),
      RESPOSTA_EM_EVENTOS,
    );
    renderizarApp(`/disciplinas/${ESTRUTURAS.id}/tutor`);

    fireEvent.click(
      await screen.findByRole('button', {
        name: 'Quais são as ideias principais da aula 5, Pilhas e filas?',
      }),
    );

    const conversa = await screen.findByRole('list', { name: 'Conversa com o tutor' });
    expect(await within(conversa).findByText(/O último a entrar/)).toBeInTheDocument();
    expect(chamadas.find((c) => c.metodo === 'POST')?.corpo).toEqual({
      texto: 'Quais são as ideias principais da aula 5, Pilhas e filas?',
    });
  });

  it('em prova, avisa que o tutor está pausado e não deixa perguntar', async () => {
    simularTutor(estado({ pausado: true }));
    renderizarApp(`/disciplinas/${ESTRUTURAS.id}/tutor`);

    expect(
      await screen.findByRole('heading', { name: 'O tutor está pausado durante a prova' }),
    ).toBeInTheDocument();
    expect(screen.queryByLabelText('Sua pergunta')).not.toBeInTheDocument();
  });

  it('no limite do dia, mostra o aviso da API e devolve a pergunta ao campo', async () => {
    const aviso = 'Você chegou ao limite de 40 perguntas de hoje. O limite volta amanhã.';
    simularTutor(estado(), { status: 429, corpo: { detail: aviso } });
    renderizarApp(`/disciplinas/${ESTRUTURAS.id}/tutor`);

    await enviarPergunta('E uma fila?');

    expect(await screen.findByRole('alert')).toHaveTextContent(aviso);
    expect(screen.getByLabelText('Sua pergunta')).toHaveValue('E uma fila?');
    expect(screen.queryByText('E uma fila?', { selector: 'li *' })).not.toBeInTheDocument();
  });

  it('não envia pergunta vazia', async () => {
    const { chamadas } = simularTutor(estado());
    renderizarApp(`/disciplinas/${ESTRUTURAS.id}/tutor`);

    await enviarPergunta('   ');

    expect(await screen.findByRole('alert')).toHaveTextContent(
      'Escreva uma pergunta antes de enviar.',
    );
    expect(chamadas.some((c) => c.metodo === 'POST')).toBe(false);
  });

  it('mostra a resposta como texto, sem interpretar HTML', async () => {
    simularTutor(
      estado({
        mensagens: [
          { id: 1, autor: 'tutor', tipo: 'resposta', texto: '<b>negrito</b> [1]', citacoes: [] },
        ],
      }),
    );
    const { container } = renderizarApp(`/disciplinas/${ESTRUTURAS.id}/tutor`);

    expect(await screen.findByText('<b>negrito</b> [1]')).toBeInTheDocument();
    expect(container.querySelector('b')).toBeNull();
  });

  it('a lista de disciplinas da aluna leva ao tutor de cada disciplina', async () => {
    simularTutor(estado());
    const { roteador } = renderizarApp('/disciplinas');

    fireEvent.click(await screen.findByRole('link', { name: 'Tutor de Estruturas de Dados' }));

    await waitFor(() =>
      expect(roteador.state.location.pathname).toBe(`/disciplinas/${ESTRUTURAS.id}/tutor`),
    );
  });

  it('a aluna marca a resposta como incorreta, vê o agradecimento e pode desfazer', async () => {
    const { chamadas } = simularApi({
      'GET /api/eu': { corpo: ANA },
      'GET /api/disciplinas': { corpo: DISCIPLINAS },
      [`GET ${URL_DO_TUTOR}`]: { corpo: CONVERSA_GUARDADA },
      'PUT /api/mensagens/2/avaliacao': { status: 204 },
    });
    renderizarApp(`/disciplinas/${ESTRUTURAS.id}/tutor`);

    const avaliar = await screen.findByRole('group', { name: 'Avaliar resposta' });
    const incorreta = within(avaliar).getByRole('button', { name: 'Incorreta' });
    fireEvent.click(incorreta);

    await waitFor(() => expect(incorreta).toHaveAttribute('aria-pressed', 'true'));
    expect(
      screen.getByText('Obrigado. Respostas marcadas como incorretas vão para revisão da equipe.'),
    ).toBeInTheDocument();
    fireEvent.click(incorreta);
    await waitFor(() => expect(incorreta).toHaveAttribute('aria-pressed', 'false'));
    expect(chamadas.filter((c) => c.metodo === 'PUT').map((c) => c.corpo)).toEqual([
      { avaliacao: 'incorreta' },
      { avaliacao: '' },
    ]);
  });

  it('a resposta nova também pode ser avaliada', async () => {
    simularTutor(estado(), RESPOSTA_EM_EVENTOS);
    renderizarApp(`/disciplinas/${ESTRUTURAS.id}/tutor`);

    await enviarPergunta('O que é uma pilha?');

    expect(await screen.findByRole('group', { name: 'Avaliar resposta' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Útil' })).toHaveAttribute('aria-pressed', 'false');
  });

  it('a resposta "não encontrei" não tem avaliação', async () => {
    simularTutor(
      estado({
        mensagens: [
          {
            id: 3,
            autor: 'tutor',
            tipo: 'nao_encontrado',
            texto: 'Não encontrei isso no material da disciplina.',
            citacoes: [],
          },
        ],
      }),
    );
    renderizarApp(`/disciplinas/${ESTRUTURAS.id}/tutor`);

    await screen.findByText('Não encontrei isso no material da disciplina.');
    expect(screen.queryByRole('group', { name: 'Avaliar resposta' })).not.toBeInTheDocument();
  });

  it('mostra a política do professor e o resumo das regras ao tocar no botão', async () => {
    simularTutor(estado({ politica: 'Use o tutor para estudar, não para copiar.' }));
    const { container } = renderizarApp(`/disciplinas/${ESTRUTURAS.id}/tutor`);

    const botao = await screen.findByRole('button', { name: 'Política de uso de IA' });
    expect(botao).toHaveAttribute('aria-expanded', 'false');
    fireEvent.click(botao);

    const politica = screen.getByRole('region', { name: 'Política de uso de IA' });
    expect(botao).toHaveAttribute('aria-expanded', 'true');
    expect(within(politica).getByText('Use o tutor para estudar, não para copiar.')).toBeVisible();
    expect(within(politica).getByText(/só com o material desta disciplina/)).toBeVisible();
    expect(within(politica).getByText(/dá pistas em vez da resposta pronta/)).toBeVisible();
    expect(within(politica).getByText('Fica pausado durante as provas.')).toBeVisible();
    expect(await violacoesDeAcessibilidade(container)).toEqual([]);
  });

  it('a política também aparece com o tutor pausado, e avisa quando não foi escrita', async () => {
    simularTutor(estado({ pausado: true, modo_pistas: false }));
    renderizarApp(`/disciplinas/${ESTRUTURAS.id}/tutor`);

    fireEvent.click(await screen.findByRole('button', { name: 'Política de uso de IA' }));

    const politica = screen.getByRole('region', { name: 'Política de uso de IA' });
    expect(
      within(politica).getByText(
        'O professor ainda não escreveu uma política para esta disciplina.',
      ),
    ).toBeVisible();
    expect(
      within(politica).getByText('O modo pistas está desligado nesta disciplina.'),
    ).toBeVisible();
  });

  it('mostra a dúvida já enviada ao professor e o status dela (DUV-T31)', async () => {
    simularTutor(
      estado({
        mensagens: [
          { id: 1, autor: 'aluno', texto: 'Isso cai na prova?', citacoes: [] },
          {
            id: 2,
            autor: 'tutor',
            tipo: 'nao_encontrado',
            texto: 'Não encontrei isso no material da disciplina.',
            citacoes: [],
          },
        ],
      }),
      undefined,
      [{ mensagem_id: 2, status: 'respondida' }],
    );
    renderizarApp(`/disciplinas/${ESTRUTURAS.id}/tutor`);

    expect(
      await screen.findByText('Dúvida enviada ao professor, sem o seu nome.'),
    ).toBeInTheDocument();
    expect(screen.getByText('O professor marcou como respondida em aula.')).toBeInTheDocument();
  });

  it('envia a dúvida do "não encontrei" depois de mostrar a prévia (DUV-T12)', async () => {
    let enviada = false;
    const { chamadas } = simularApi({
      'GET /api/eu': { corpo: ANA },
      'GET /api/disciplinas': { corpo: DISCIPLINAS },
      [`GET ${URL_DO_TUTOR}`]: {
        corpo: estado({
          mensagens: [
            { id: 1, autor: 'aluno', texto: 'Sou [nome], isso cai na prova?', citacoes: [] },
            {
              id: 2,
              autor: 'tutor',
              tipo: 'nao_encontrado',
              texto: 'Não encontrei isso no material da disciplina.',
              citacoes: [],
            },
          ],
        }),
      },
      [`GET /api/disciplinas/${ESTRUTURAS.id}/minhas-duvidas`]: () => ({
        corpo: enviada ? [{ mensagem_id: 2, status: 'aberta' }] : [],
      }),
      'POST /api/mensagens/2/duvida/previa': {
        corpo: { texto_filtrado: 'Sou [nome], isso cai na prova?' },
      },
      'POST /api/mensagens/2/duvida': () => {
        enviada = true;
        return { status: 201, corpo: { duvida_id: 5, status: 'aberta' } };
      },
    });
    const { container } = renderizarApp(`/disciplinas/${ESTRUTURAS.id}/tutor`);

    fireEvent.click(await screen.findByRole('button', { name: 'Enviar dúvida ao professor' }));

    const dialogo = await screen.findByRole('dialog', { name: 'Enviar dúvida ao professor' });
    expect(within(dialogo).getByText('Sou [nome], isso cai na prova?')).toBeVisible();
    expect(within(dialogo).getByText(/não verá o seu nome/)).toBeVisible();
    expect(chamadas.some((c) => c.caminho === '/api/mensagens/2/duvida')).toBe(false);
    expect(await violacoesDeAcessibilidade(container)).toEqual([]);

    fireEvent.click(within(dialogo).getByRole('button', { name: 'Enviar ao professor' }));

    expect(
      await screen.findByText('Dúvida enviada ao professor, sem o seu nome.', { selector: 'li *' }),
    ).toBeInTheDocument();
    expect(screen.queryByRole('dialog')).toBeNull();
    expect(screen.queryByRole('button', { name: 'Enviar dúvida ao professor' })).toBeNull();
  });

  it('cancelar a prévia não envia nada', async () => {
    const { chamadas } = simularApi({
      'GET /api/eu': { corpo: ANA },
      'GET /api/disciplinas': { corpo: DISCIPLINAS },
      [`GET ${URL_DO_TUTOR}`]: {
        corpo: estado({
          mensagens: [
            { id: 1, autor: 'aluno', texto: 'Isso cai na prova?', citacoes: [] },
            {
              id: 2,
              autor: 'tutor',
              tipo: 'nao_encontrado',
              texto: 'Não encontrei isso no material da disciplina.',
              citacoes: [],
            },
          ],
        }),
      },
      [`GET /api/disciplinas/${ESTRUTURAS.id}/minhas-duvidas`]: { corpo: [] },
      'POST /api/mensagens/2/duvida/previa': { corpo: { texto_filtrado: 'Isso cai na prova?' } },
    });
    renderizarApp(`/disciplinas/${ESTRUTURAS.id}/tutor`);

    fireEvent.click(await screen.findByRole('button', { name: 'Enviar dúvida ao professor' }));
    fireEvent.click(await screen.findByRole('button', { name: 'Cancelar' }));

    await waitFor(() => expect(screen.queryByRole('dialog')).toBeNull());
    expect(chamadas.some((c) => c.caminho === '/api/mensagens/2/duvida')).toBe(false);
  });
});
