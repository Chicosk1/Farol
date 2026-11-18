import type { ReactNode } from 'react';

import { Icone } from './Icone';
import type { NomeDoIcone } from './icones';

export type TomDoSelo = 'neutro' | 'destaque' | 'sucesso' | 'atencao' | 'perigo' | 'amarelo';

const TONS: Record<TomDoSelo, string> = {
  neutro: '',
  destaque: 'fr-badge--accent',
  sucesso: 'fr-badge--success',
  atencao: 'fr-badge--warning',
  perigo: 'fr-badge--danger',
  amarelo: 'fr-badge--highlight',
};

type Props = { tom?: TomDoSelo; pilula?: boolean; icone?: NomeDoIcone; children: ReactNode };

/** Selo curto de estado ou categoria (classe fr-badge do protótipo). */
export function Selo({ tom = 'neutro', pilula = false, icone, children }: Props) {
  const classes = ['fr-badge', TONS[tom], pilula ? 'fr-badge--pill' : ''].filter(Boolean);
  return (
    <span className={classes.join(' ')}>
      {icone && <Icone nome={icone} />}
      {children}
    </span>
  );
}
