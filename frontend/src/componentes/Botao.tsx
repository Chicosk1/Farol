import type { ButtonHTMLAttributes, ReactNode } from 'react';

import { classesDoBotao, type VarianteDoBotao } from './classes';
import { Icone } from './Icone';
import type { NomeDoIcone } from './icones';

type Props = ButtonHTMLAttributes<HTMLButtonElement> & {
  variante?: VarianteDoBotao;
  pequeno?: boolean;
  icone?: NomeDoIcone;
  children?: ReactNode;
};

/** Botão do design system Farol (classe fr-btn do protótipo). */
export function Botao({
  variante = 'primario',
  pequeno = false,
  icone,
  className = '',
  type = 'button',
  children,
  ...resto
}: Props) {
  return (
    <button
      type={type}
      className={`${classesDoBotao(variante, pequeno)} ${className}`.trim()}
      {...resto}
    >
      {icone && <Icone nome={icone} />}
      {children}
    </button>
  );
}
