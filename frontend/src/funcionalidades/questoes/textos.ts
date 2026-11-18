export const LETRAS = ['A', 'B', 'C', 'D'] as const;

/** O endereço do tutor da disciplina com uma pergunta já escrita na caixa (QUE-RF-09). */
export function tutorComPergunta(disciplinaId: number, pergunta: string): string {
  return `/disciplinas/${disciplinaId}/tutor?pergunta=${encodeURIComponent(pergunta)}`;
}
