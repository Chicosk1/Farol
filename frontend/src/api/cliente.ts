/**
 * Único caminho entre as telas e a API do Farol (ADR 0007). Os tipos vêm de esquema.d.ts,
 * gerado do contrato OpenAPI do back-end com `npm run api:gerar`: se a API muda, a compilação avisa.
 * A sessão é o cookie do Django, na mesma origem (sem JWT); as chamadas que mudam dados levam o
 * token CSRF no cabeçalho X-CSRFToken.
 */
import type { components } from './esquema';

export type Saude = components['schemas']['Saude'];
export type Eu = components['schemas']['Eu'];
export type FormasDeEntrar = components['schemas']['FormasDeEntrar'];
export type Perfil = components['schemas']['PerfilEnum'];
export type Disciplina = components['schemas']['Disciplina'];
export type AvisoDePrivacidade = components['schemas']['AvisoDePrivacidade'];
export type FiltroDeDisciplinas = 'todas' | 'favoritas' | 'com-tutor';
export type MaterialDoProfessor = components['schemas']['MaterialDoProfessor'];
export type Notificacoes = components['schemas']['Notificacoes'];
export type Notificacao = components['schemas']['Notificacao'];
export type EstadoDoTutor = components['schemas']['EstadoDoTutor'];
export type MensagemDoTutor = components['schemas']['Mensagem'];
export type CitacaoDoTutor = components['schemas']['Citacao'];
export type TipoDeMensagem = components['schemas']['MensagemTipoEnum'];
export type ConfiguracaoDoTutor = components['schemas']['Configuracao'];
export type JanelaDeProva = components['schemas']['Janela'];
/** A avaliação de uma resposta do tutor; vazio é sem avaliação. */
export type AvaliacaoDaResposta = components['schemas']['AvaliacaoEnum'] | '';

/** Os eventos da resposta do tutor em streaming (SSE), na ordem em que chegam. */
export type EventoDoTutor =
  | { evento: 'inicio'; dados: { conversa_id: number } }
  | { evento: 'texto'; dados: { texto: string } }
  | { evento: 'citacao'; dados: CitacaoDoTutor }
  | { evento: 'fim'; dados: { tipo: TipoDeMensagem; mensagem_id: number } }
  | { evento: 'erro'; dados: { mensagem: string } };

/** Resposta da API fora da faixa de sucesso (2xx), com o status e o corpo devolvidos. */
export class ErroDaApi extends Error {
  readonly status: number;
  readonly corpo: unknown;

  constructor(status: number, corpo: unknown) {
    super(`A API do Farol respondeu com o status ${status}.`);
    this.name = 'ErroDaApi';
    this.status = status;
    this.corpo = corpo;
  }
}

async function lerCorpo(resposta: Response): Promise<unknown> {
  const texto = await resposta.text();
  if (!texto) {
    return undefined;
  }
  try {
    return JSON.parse(texto);
  } catch {
    return texto;
  }
}

/** Token CSRF que o Django entrega no cookie `csrftoken` (por exemplo, em GET /api/eu). */
export function tokenCsrf(): string | undefined {
  const cookie = document.cookie.split('; ').find((parte) => parte.startsWith('csrftoken='));
  return cookie ? decodeURIComponent(cookie.slice('csrftoken='.length)) : undefined;
}

async function requisitar<T>(caminho: string, opcoes: RequestInit = {}): Promise<T> {
  const metodo = (opcoes.method ?? 'GET').toUpperCase();
  const cabecalhos = new Headers({ Accept: 'application/json' });
  if (opcoes.body !== undefined) {
    cabecalhos.set('Content-Type', 'application/json');
  }
  const csrf = tokenCsrf();
  if (metodo !== 'GET' && csrf) {
    cabecalhos.set('X-CSRFToken', csrf);
  }
  const resposta = await fetch(caminho, {
    credentials: 'same-origin',
    ...opcoes,
    method: metodo,
    headers: cabecalhos,
  });
  const corpo = await lerCorpo(resposta);
  if (!resposta.ok) {
    throw new ErroDaApi(resposta.status, corpo);
  }
  return corpo as T;
}

function enviar<T>(caminho: string, dados?: unknown, metodo = 'POST'): Promise<T> {
  return requisitar<T>(caminho, {
    method: metodo,
    body: dados === undefined ? undefined : JSON.stringify(dados),
  });
}

/** GET /api/saude: diz se a API está no ar. */
export function obterSaude(): Promise<Saude> {
  return requisitar<Saude>('/api/saude');
}

/** GET /api/eu: a pessoa logada, ou null quando ninguém entrou (401). */
export async function obterEu(): Promise<Eu | null> {
  try {
    return await requisitar<Eu>('/api/eu');
  } catch (erro) {
    if (erro instanceof ErroDaApi && erro.status === 401) {
      return null;
    }
    throw erro;
  }
}

/**
 * Ida ao Google pelo django-allauth (ACE-RF-01). Não é uma chamada da API: a tela envia um
 * formulário para este endereço, e o navegador segue até o Google e volta ao Farol.
 */
export const ENDERECO_DO_LOGIN_GOOGLE = '/contas/google/login/';

/** GET /api/entrada: as formas de entrar neste ambiente. Também entrega o cookie CSRF. */
export function obterFormasDeEntrar(): Promise<FormasDeEntrar> {
  return requisitar<FormasDeEntrar>('/api/entrada');
}

/** POST /api/dev/entrar: só existe em desenvolvimento e em teste (ACE-RNF-03). */
export function entrarEmDesenvolvimento(email: string): Promise<Eu> {
  return enviar<Eu>('/api/dev/entrar', { email });
}

/** POST /api/eu/perfil-ativo: troca o perfil em uso, sem sair. */
export function trocarPerfilAtivo(perfil: Perfil): Promise<Eu> {
  return enviar<Eu>('/api/eu/perfil-ativo', { perfil });
}

/** GET /api/disciplinas/{id}: uma disciplina da pessoa, com os mesmos dados da lista. */
export function obterDisciplina(id: number | string): Promise<Disciplina> {
  return requisitar<Disciplina>(`/api/disciplinas/${id}`);
}

/** GET /api/disciplinas: as disciplinas da pessoa no perfil em uso, com busca e filtro. */
export function listarDisciplinas(
  opcoes: { busca?: string; filtro?: FiltroDeDisciplinas } = {},
): Promise<Disciplina[]> {
  const consulta = new URLSearchParams();
  const busca = opcoes.busca?.trim();
  if (busca) {
    consulta.set('busca', busca);
  }
  if (opcoes.filtro && opcoes.filtro !== 'todas') {
    consulta.set('filtro', opcoes.filtro);
  }
  const texto = consulta.toString();
  return requisitar<Disciplina[]>(texto ? `/api/disciplinas?${texto}` : '/api/disciplinas');
}

/** PUT ou DELETE /api/disciplinas/{id}/favorito: marca ou desmarca a disciplina como favorita. */
export async function definirFavorito(disciplinaId: number, favorita: boolean): Promise<void> {
  await enviar<undefined>(
    `/api/disciplinas/${disciplinaId}/favorito`,
    undefined,
    favorita ? 'PUT' : 'DELETE',
  );
}

/** GET /api/aviso-privacidade: a versão atual do aviso e o seu texto. */
export function obterAvisoDePrivacidade(): Promise<AvisoDePrivacidade> {
  return requisitar<AvisoDePrivacidade>('/api/aviso-privacidade');
}

/** POST /api/eu/ciencia-privacidade: registra que a pessoa leu esta versão do aviso. */
export async function confirmarCienciaDoAviso(versao: string): Promise<void> {
  await enviar<undefined>('/api/eu/ciencia-privacidade', { versao });
}

/** POST /api/sair: encerra a sessão. */
export async function sair(): Promise<void> {
  await enviar<undefined>('/api/sair');
}

/** GET /api/disciplinas/{id}/tutor: regras, pausa, uso do dia, conversa guardada e sugestões. */
export function obterTutor(disciplinaId: number): Promise<EstadoDoTutor> {
  return requisitar<EstadoDoTutor>(`/api/disciplinas/${disciplinaId}/tutor`);
}

function lerEvento(bloco: string): EventoDoTutor | null {
  let evento = '';
  let dados = '';
  for (const linha of bloco.split('\n')) {
    if (linha.startsWith('event: ')) evento = linha.slice('event: '.length);
    else if (linha.startsWith('data: ')) dados += linha.slice('data: '.length);
  }
  return evento && dados ? ({ evento, dados: JSON.parse(dados) } as EventoDoTutor) : null;
}

/**
 * POST /api/disciplinas/{id}/tutor/perguntas: envia a pergunta e entrega cada evento da resposta
 * assim que ele chega. Recusas antes da resposta (400, 423, 429, 503) viram ErroDaApi.
 */
export async function perguntarAoTutor(
  disciplinaId: number,
  texto: string,
  aoReceber: (evento: EventoDoTutor) => void,
): Promise<void> {
  const cabecalhos = new Headers({
    Accept: 'text/event-stream',
    'Content-Type': 'application/json',
  });
  const csrf = tokenCsrf();
  if (csrf) {
    cabecalhos.set('X-CSRFToken', csrf);
  }
  const resposta = await fetch(`/api/disciplinas/${disciplinaId}/tutor/perguntas`, {
    method: 'POST',
    credentials: 'same-origin',
    headers: cabecalhos,
    body: JSON.stringify({ texto }),
  });
  if (!resposta.ok || !resposta.body) {
    throw new ErroDaApi(resposta.status, await lerCorpo(resposta));
  }
  const leitor = resposta.body.getReader();
  const decodificador = new TextDecoder();
  let pendente = '';
  for (;;) {
    const { value, done } = await leitor.read();
    pendente += done ? decodificador.decode() : decodificador.decode(value, { stream: true });
    const blocos = pendente.split('\n\n');
    pendente = done ? '' : (blocos.pop() ?? '');
    for (const bloco of blocos) {
      const evento = lerEvento(bloco);
      if (evento) aoReceber(evento);
    }
    if (done) return;
  }
}

/** PUT /api/mensagens/{id}/avaliacao: marca a resposta; vazio desfaz a marcação (TUT-RF-09). */
export async function avaliarResposta(
  mensagemId: number,
  avaliacao: AvaliacaoDaResposta,
): Promise<void> {
  await enviar<undefined>(`/api/mensagens/${mensagemId}/avaliacao`, { avaliacao }, 'PUT');
}

/** GET /api/disciplinas/{id}/tutor/configuracao: modo pistas, limite e política (professor). */
export function obterConfiguracaoDoTutor(disciplinaId: number): Promise<ConfiguracaoDoTutor> {
  return requisitar<ConfiguracaoDoTutor>(`/api/disciplinas/${disciplinaId}/tutor/configuracao`);
}

/** PATCH /api/disciplinas/{id}/tutor/configuracao: só os campos enviados mudam. */
export function salvarConfiguracaoDoTutor(
  disciplinaId: number,
  mudancas: ConfiguracaoDoTutor,
): Promise<ConfiguracaoDoTutor> {
  return enviar<ConfiguracaoDoTutor>(
    `/api/disciplinas/${disciplinaId}/tutor/configuracao`,
    mudancas,
    'PATCH',
  );
}

/** GET /api/disciplinas/{id}/janelas-prova: a janela em andamento e as agendadas (professor). */
export function listarJanelasDeProva(disciplinaId: number): Promise<JanelaDeProva[]> {
  return requisitar<JanelaDeProva[]>(`/api/disciplinas/${disciplinaId}/janelas-prova`);
}

/** POST /api/disciplinas/{id}/janelas-prova: sem início, pausa o tutor agora (modo prova). */
export function criarJanelaDeProva(
  disciplinaId: number,
  dados: { inicio?: string; fim?: string },
): Promise<JanelaDeProva> {
  return enviar<JanelaDeProva>(`/api/disciplinas/${disciplinaId}/janelas-prova`, dados);
}

/** DELETE /api/disciplinas/{id}/janelas-prova/{janela}: apaga a janela (desliga o modo prova). */
export async function apagarJanelaDeProva(disciplinaId: number, janelaId: number): Promise<void> {
  await enviar<undefined>(
    `/api/disciplinas/${disciplinaId}/janelas-prova/${janelaId}`,
    undefined,
    'DELETE',
  );
}

/** GET /api/disciplinas/{id}/materiais: para o professor, todos, com status e etapa. */
export function listarMateriaisDoProfessor(disciplinaId: number): Promise<MaterialDoProfessor[]> {
  return requisitar<MaterialDoProfessor[]>(`/api/disciplinas/${disciplinaId}/materiais`);
}

/** POST /api/disciplinas/{id}/materiais (multipart): envia o PDF; o processamento vai para a fila. */
export async function enviarMaterial(
  disciplinaId: number,
  dados: { arquivo: File; aulaNumero: number; aulaTitulo: string },
): Promise<void> {
  const formulario = new FormData();
  formulario.append('arquivo', dados.arquivo);
  formulario.append('aula_numero', String(dados.aulaNumero));
  formulario.append('aula_titulo', dados.aulaTitulo);
  const cabecalhos = new Headers({ Accept: 'application/json' });
  const csrf = tokenCsrf();
  if (csrf) {
    cabecalhos.set('X-CSRFToken', csrf);
  }
  // Sem Content-Type: o navegador põe o multipart com a fronteira certa.
  const resposta = await fetch(`/api/disciplinas/${disciplinaId}/materiais`, {
    method: 'POST',
    credentials: 'same-origin',
    headers: cabecalhos,
    body: formulario,
  });
  if (!resposta.ok) {
    throw new ErroDaApi(resposta.status, await lerCorpo(resposta));
  }
}

/** POST /api/materiais/{id}/versoes (multipart): a versão nova substitui a anterior quando fica pronta. */
export async function enviarNovaVersao(materialId: number, arquivo: File): Promise<void> {
  const formulario = new FormData();
  formulario.append('arquivo', arquivo);
  const cabecalhos = new Headers({ Accept: 'application/json' });
  const csrf = tokenCsrf();
  if (csrf) {
    cabecalhos.set('X-CSRFToken', csrf);
  }
  const resposta = await fetch(`/api/materiais/${materialId}/versoes`, {
    method: 'POST',
    credentials: 'same-origin',
    headers: cabecalhos,
    body: formulario,
  });
  if (!resposta.ok) {
    throw new ErroDaApi(resposta.status, await lerCorpo(resposta));
  }
}

/** DELETE /api/materiais/{id}: retira o material; o tutor deixa de usá-lo (MAT-RF-10). */
export async function retirarMaterial(materialId: number): Promise<void> {
  await enviar<undefined>(`/api/materiais/${materialId}`, undefined, 'DELETE');
}

/** GET /api/notificacoes: as notificações mais recentes e quantas não foram lidas. */
export function listarNotificacoes(): Promise<Notificacoes> {
  return requisitar<Notificacoes>('/api/notificacoes');
}

/** POST /api/notificacoes/{id}/lida. */
export async function marcarNotificacaoComoLida(notificacaoId: number): Promise<void> {
  await enviar<undefined>(`/api/notificacoes/${notificacaoId}/lida`);
}

export type MinhaDuvida = components['schemas']['MinhaDuvida'];

/** GET /api/disciplinas/{id}/minhas-duvidas: as dúvidas que o aluno enviou e o status de cada uma. */
export function listarMinhasDuvidas(disciplinaId: number): Promise<MinhaDuvida[]> {
  return requisitar<MinhaDuvida[]>(`/api/disciplinas/${disciplinaId}/minhas-duvidas`);
}

/** POST /api/mensagens/{id}/duvida/previa: o texto exato que vai ao professor (DUV-RF-02). */
export async function previaDaDuvida(mensagemId: number): Promise<string> {
  const previa = await enviar<{ texto_filtrado: string }>(
    `/api/mensagens/${mensagemId}/duvida/previa`,
  );
  return previa.texto_filtrado;
}

/** POST /api/mensagens/{id}/duvida: envia a dúvida ao professor, sem o nome do aluno. */
export async function enviarDuvida(mensagemId: number): Promise<void> {
  await enviar<unknown>(`/api/mensagens/${mensagemId}/duvida`);
}

export type DuvidaDoProfessor = components['schemas']['DuvidaDoProfessor'];

/** GET /api/disciplinas/{id}/duvidas: as dúvidas abertas ou respondidas, sem dados dos alunos. */
export function listarDuvidasDaDisciplina(
  disciplinaId: number,
  status: 'aberta' | 'respondida',
): Promise<DuvidaDoProfessor[]> {
  return requisitar<DuvidaDoProfessor[]>(
    `/api/disciplinas/${disciplinaId}/duvidas?status=${status}`,
  );
}

/** PATCH /api/disciplinas/{id}/duvidas/{duvida}: respondida em aula ou oculta (DUV-RF-07). */
export function mudarStatusDaDuvida(
  disciplinaId: number,
  duvidaId: number,
  status: 'respondida' | 'oculta',
): Promise<DuvidaDoProfessor> {
  return enviar<DuvidaDoProfessor>(
    `/api/disciplinas/${disciplinaId}/duvidas/${duvidaId}`,
    { status },
    'PATCH',
  );
}

/** O que a aluna vê de um material: só os prontos, sem status, etapa nem erro. */
export type MaterialDoAluno = Pick<
  MaterialDoProfessor,
  'id' | 'aula_numero' | 'aula_titulo' | 'paginas'
>;

/** GET /api/disciplinas/{id}/materiais: para a aluna, só os materiais prontos (MAT-RF-08). */
export function listarMateriaisDoAluno(disciplinaId: number): Promise<MaterialDoAluno[]> {
  return requisitar<MaterialDoAluno[]>(`/api/disciplinas/${disciplinaId}/materiais`);
}

export type ConversaDoHistorico = components['schemas']['ConversaDoHistorico'];

/** GET /api/eu/historico: as conversas do aluno com o tutor, por disciplina (ACE-RF-09). */
export function obterHistorico(): Promise<ConversaDoHistorico[]> {
  return requisitar<ConversaDoHistorico[]>('/api/eu/historico');
}

/** DELETE /api/eu/historico: apaga todas as conversas do aluno com o tutor. */
export async function apagarHistorico(): Promise<void> {
  await enviar<undefined>('/api/eu/historico', undefined, 'DELETE');
}

export type TrechoParaAbrir = components['schemas']['TrechoParaAbrir'];

/** GET /api/trechos/{id}: a página citada com a posição do trecho, para destacar (MAT-RF-09). */
export function obterTrecho(trechoId: number): Promise<TrechoParaAbrir> {
  return requisitar<TrechoParaAbrir>(`/api/trechos/${trechoId}`);
}

export type QuestaoDoProfessor = components['schemas']['QuestaoDoProfessor'];
export type QuestoesDaDisciplina = components['schemas']['QuestoesDaDisciplina'];
export type StatusDaQuestao = QuestaoDoProfessor['status'];
export type Geracao = components['schemas']['Geracao'];
export type Quiz = components['schemas']['Quiz'];
export type RetornoDaQuestao = components['schemas']['RetornoDaQuestao'];
export type QuizDaAula = components['schemas']['QuizDaAula'];
/** O que o professor muda numa questão: o conteúdo (só em pendentes) e, ou, o status. */
export type MudancaDeQuestao = Partial<
  Pick<
    QuestaoDoProfessor,
    'enunciado' | 'alternativas' | 'correta' | 'justificativa' | 'topico' | 'status'
  >
>;

/** GET /api/disciplinas/{id}/questoes: as questões de um status e as contagens (QUE-RF-06). */
export function listarQuestoes(
  disciplinaId: number,
  status: StatusDaQuestao,
): Promise<QuestoesDaDisciplina> {
  return requisitar<QuestoesDaDisciplina>(
    `/api/disciplinas/${disciplinaId}/questoes?status=${status}`,
  );
}

/** PATCH /api/questoes/{id}: aprova, edita, descarta ou devolve para pendentes (QUE-RF-05). */
export function mudarQuestao(
  questaoId: number,
  dados: MudancaDeQuestao,
): Promise<QuestaoDoProfessor> {
  return enviar<QuestaoDoProfessor>(`/api/questoes/${questaoId}`, dados, 'PATCH');
}

/** POST /api/materiais/{id}/geracoes: pede de 5 a 20 rascunhos de uma aula (QUE-RF-01). */
export function pedirGeracao(materialId: number, quantidade: number): Promise<Geracao> {
  return enviar<Geracao>(`/api/materiais/${materialId}/geracoes`, { quantidade });
}

/** GET /api/geracoes/{id}: o andamento do pedido de rascunhos. */
export function obterGeracao(pedidoId: number): Promise<Geracao> {
  return requisitar<Geracao>(`/api/geracoes/${pedidoId}`);
}

/** GET /api/materiais/{id}/quiz: as questões publicadas da aula, sem o gabarito (QUE-RF-04). */
export function obterQuiz(materialId: number): Promise<Quiz> {
  return requisitar<Quiz>(`/api/materiais/${materialId}/quiz`);
}

/** POST /api/questoes/{id}/respostas: corrige e devolve o retorno da questão (QUE-RF-08). */
export function responderQuestao(
  questaoId: number,
  alternativa: number,
): Promise<RetornoDaQuestao> {
  return enviar<RetornoDaQuestao>(`/api/questoes/${questaoId}/respostas`, { alternativa });
}

/** POST /api/materiais/{id}/quiz/reiniciar: começa o quiz da aula de novo. */
export async function reiniciarQuiz(materialId: number): Promise<void> {
  await enviar<undefined>(`/api/materiais/${materialId}/quiz/reiniciar`);
}

/** GET /api/disciplinas/{id}/quizzes: as aulas com quiz e o andamento do aluno. */
export function listarQuizzes(disciplinaId: number): Promise<QuizDaAula[]> {
  return requisitar<QuizDaAula[]>(`/api/disciplinas/${disciplinaId}/quizzes`);
}
