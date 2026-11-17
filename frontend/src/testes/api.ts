import { vi } from 'vitest';

export type RespostaSimulada = { status?: number; corpo?: unknown };
type Rota = RespostaSimulada | ((chamada: ChamadaSimulada) => RespostaSimulada);

export type ChamadaSimulada = {
  metodo: string;
  caminho: string;
  corpo: unknown;
  /** Os campos de um envio multipart; arquivos aparecem pelo nome. */
  formulario?: Record<string, string>;
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
      formulario:
        init.body instanceof FormData
          ? Object.fromEntries(
              [...init.body.entries()].map(([campo, valor]) => [
                campo,
                typeof valor === 'string' ? valor : valor.name,
              ]),
            )
          : undefined,
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
  precisa_ver_aviso: false,
} as const;

/** A Ana na primeira entrada, antes de ler o aviso de privacidade. */
export const ANA_NOVA = { ...ANA, precisa_ver_aviso: true } as const;

export const CARLOS = {
  id: 2,
  email: 'carlos.mendes@exemplo.edu.br',
  nome: 'Carlos Mendes',
  perfis: ['professor'],
  perfil_ativo: 'professor',
  precisa_ver_aviso: false,
} as const;

/** As seis disciplinas do 2º período do protótipo, no formato de GET /api/disciplinas. */
export const DISCIPLINAS = [
  ['Álgebra Linear', 'SINF205', 'Rogério Lima'],
  ['Banco de Dados I', 'SINF202', 'Marta Ribeiro'],
  ['Engenharia de Software I', 'SINF206', 'Paulo Nunes'],
  ['Estruturas de Dados', 'SINF201', 'Carlos Mendes'],
  ['Matemática Discreta', 'SINF204', 'Luciana Alves'],
  ['Programação Orientada a Objetos', 'SINF203', 'João Pereira'],
].map(([nome, codigo, professor_nome], i) => ({
  id: i + 1,
  codigo,
  nome,
  turma: 'SINF2NA',
  semestre: '2026/2',
  professor_nome,
  favorita: false,
}));

/** A página inicial pede as disciplinas favoritas; testes que não tratam delas usam esta rota. */
export const FAVORITAS_VAZIAS = {
  'GET /api/disciplinas?filtro=favoritas': { corpo: [] },
} as const;

/** GET /api/aviso-privacidade. */
export const AVISO = {
  versao: '1',
  titulo: 'Como o Farol cuida dos seus dados',
  itens: [
    { titulo: 'O que é registrado', texto: 'O seu nome, o seu e-mail e as suas disciplinas.' },
    { titulo: 'Para quê', texto: 'Para mostrar só as suas disciplinas.' },
    { titulo: 'Por quanto tempo', texto: 'As perguntas são guardadas por 12 meses.' },
    { titulo: 'Os seus direitos', texto: 'Você pode ver e apagar o seu histórico.' },
  ],
};
