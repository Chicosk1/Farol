import type { ButtonHTMLAttributes } from 'react';

type Variante = 'primario' | 'secundario';

const BASE =
  'inline-flex min-h-12 items-center justify-center rounded-lg px-4 text-sm font-bold ' +
  'disabled:cursor-not-allowed disabled:opacity-60';

const VARIANTES: Record<Variante, string> = {
  primario: 'bg-accent text-on-accent',
  secundario: 'border border-line-control bg-surface text-ink',
};

type Props = ButtonHTMLAttributes<HTMLButtonElement> & { variante?: Variante };

/** Botão do design system Farol: 48 px de altura, foco visível pelo estilo global. */
export function Botao({ variante = 'primario', className = '', type = 'button', ...resto }: Props) {
  return (
    <button type={type} className={`${BASE} ${VARIANTES[variante]} ${className}`} {...resto} />
  );
}
