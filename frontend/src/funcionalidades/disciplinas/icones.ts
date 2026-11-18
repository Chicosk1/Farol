import type { NomeDoIcone } from '../../componentes/icones';

/** Palavras do nome da disciplina e o ícone que a representa, como no protótipo. */
const ICONES_POR_ASSUNTO: [RegExp, NomeDoIcone][] = [
  [/estrutura|algoritm|grafo/i, 'binary-tree'],
  [/banco de dados|dados/i, 'database'],
  [/program|orientad|c[oó]digo|web|compila/i, 'code'],
  [/discreta|l[oó]gica|[aá]lgebra/i, 'math-symbols'],
  [/c[aá]lculo|matem|estat[ií]stic/i, 'math-function'],
  [/engenharia|software|projeto/i, 'git-branch'],
  [/rede|sistemas operacionais|arquitetura/i, 'device-desktop'],
];

/** O ícone do cartão da disciplina; sem assunto conhecido, um livro. */
export function iconeDaDisciplina(nome: string): NomeDoIcone {
  return ICONES_POR_ASSUNTO.find(([padrao]) => padrao.test(nome))?.[1] ?? 'book-2';
}
