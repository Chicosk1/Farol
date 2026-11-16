import { vi } from 'vitest';

export type RespostaSimulada = { status?: number; corpo?: unknown };
type Rota = RespostaSimulada | ((chamada: ChamadaSimulada) => RespostaSimulada);

export type ChamadaSimulada = {
  metodo: string;
  caminho: string;
  corpo: unknown;
  cabecalhos: Record<string, string>;
};

/**
 * Troca o fetch por uma API simulada. As rotas são chaves como 'GET /api/eu'. Uma rota que o teste
 * não descreveu falha na hora, para o teste não depender de uma chamada que ninguém previu.
 */
export function simularApi(rotas: Record<string, Rota>) {
  const chamadas: ChamadaSimulada[] = [];
  const fetchFalso = vi.fn(async (entrada: RequestInfo | URL, init: RequestInit = {}) => {
    const metodo = (init.method ?? 'GET').toUpperCase();
    const caminho = String(entrada);
    const chamada: ChamadaSimulada = {
      metodo,
      caminho,
      corpo: typeof init.body === 'string' ? JSON.parse(init.body) : undefined,
      cabecalhos: Object.fromEntries(new Headers(init.headers).entries()),
    };
    chamadas.push(chamada);

    const rota = rotas[`${metodo} ${caminho}`];
    if (!rota) {
      throw new Error(`Chamada não prevista no teste: ${metodo} ${caminho}`);
    }
    const { status = 200, corpo } = typeof rota === 'function' ? rota(chamada) : rota;
    return new Response(corpo === undefined ? null : JSON.stringify(corpo), {
      status,
      headers: { 'Content-Type': 'application/json' },
    });
  });
  vi.stubGlobal('fetch', fetchFalso);
  return { chamadas, fetchFalso };
}

/** Pessoas fictícias do protótipo, no formato de GET /api/eu. */
export const ANA = {
  id: 1,
  email: 'ana.souza@exemplo.edu.br',
  nome: 'Ana Souza',
  perfis: ['aluno'],
  perfil_ativo: 'aluno',
} as const;

export const CARLOS = {
  id: 2,
  email: 'carlos.mendes@exemplo.edu.br',
  nome: 'Carlos Mendes',
  perfis: ['professor'],
  perfil_ativo: 'professor',
} as const;
