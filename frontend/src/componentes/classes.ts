/** Funções que montam as classes do design system, para usar também em links e elementos nativos. */

/** Primário (fundo de destaque), contorno ou fantasma (só o texto), como no protótipo. */
export type VarianteDoBotao = 'primario' | 'contorno' | 'fantasma' | 'secundario';

const VARIANTES: Record<VarianteDoBotao, string> = {
  primario: 'fr-btn--primary',
  contorno: 'fr-btn--outline',
  secundario: 'fr-btn--outline', // o mesmo que contorno, nome antigo
  fantasma: 'fr-btn--ghost',
};

/** As classes do botão do design system, para usar também em links (`<Link>`) com cara de botão. */
export function classesDoBotao(variante: VarianteDoBotao = 'primario', pequeno = false): string {
  return ['fr-btn', VARIANTES[variante], pequeno ? 'fr-btn--sm' : ''].filter(Boolean).join(' ');
}

/** As iniciais do primeiro e do último nome: "Ana Souza" vira "AS". */
export function iniciais(nome: string): string {
  const partes = nome.trim().split(/\s+/).filter(Boolean);
  const primeira = partes[0]?.[0] ?? '';
  const ultima = partes.length > 1 ? (partes[partes.length - 1]?.[0] ?? '') : '';
  return (primeira + ultima).toUpperCase();
}
