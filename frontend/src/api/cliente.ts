/**
 * Único caminho entre as telas e a API do Farol (ADR 0007). Os tipos vêm de esquema.d.ts,
 * gerado do contrato OpenAPI do back-end com `npm run api:gerar`: se a API muda, a compilação avisa.
 * A sessão é o cookie do Django, na mesma origem (sem JWT); as chamadas que mudam dados levam o
 * token CSRF no cabeçalho X-CSRFToken.
 */
import type { components } from './esquema';

export type Saude = components['schemas']['Saude'];
export type Eu = components['schemas']['Eu'];
export type Perfil = components['schemas']['PerfilEnum'];
export type Disciplina = components['schemas']['Disciplina'];
export type FiltroDeDisciplinas = 'todas' | 'favoritas' | 'com-tutor';

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
function tokenCsrf(): string | undefined {
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

/** POST /api/dev/entrar: só existe em desenvolvimento e em teste (ACE-RNF-03). */
export function entrarEmDesenvolvimento(email: string): Promise<Eu> {
  return enviar<Eu>('/api/dev/entrar', { email });
}

/** POST /api/eu/perfil-ativo: troca o perfil em uso, sem sair. */
export function trocarPerfilAtivo(perfil: Perfil): Promise<Eu> {
  return enviar<Eu>('/api/eu/perfil-ativo', { perfil });
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

/** POST /api/sair: encerra a sessão. */
export async function sair(): Promise<void> {
  await enviar<undefined>('/api/sair');
}
