/**
 * Único caminho entre as telas e a API do Farol (ADR 0007). Os tipos vêm de esquema.d.ts,
 * gerado do contrato OpenAPI do back-end com `npm run api:gerar`: se a API muda, a compilação avisa.
 * A sessão é o cookie do Django, na mesma origem (sem JWT).
 */
import type { components } from './esquema';

export type Saude = components['schemas']['Saude'];

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

async function requisitar<T>(caminho: string, opcoes: RequestInit = {}): Promise<T> {
  const resposta = await fetch(caminho, {
    method: 'GET',
    credentials: 'same-origin',
    ...opcoes,
    headers: { Accept: 'application/json', ...opcoes.headers },
  });
  const corpo = await lerCorpo(resposta);
  if (!resposta.ok) {
    throw new ErroDaApi(resposta.status, corpo);
  }
  return corpo as T;
}

/** GET /api/saude: diz se a API está no ar. */
export function obterSaude(): Promise<Saude> {
  return requisitar<Saude>('/api/saude');
}
