import { iniciais } from './classes';

/** Círculo com as iniciais da pessoa (classe fr-avatar do protótipo). É decorativo. */
export function Avatar({ nome, grande = false }: { nome: string; grande?: boolean }) {
  return (
    <span className={grande ? 'fr-avatar fr-avatar--lg' : 'fr-avatar'} aria-hidden="true">
      {iniciais(nome)}
    </span>
  );
}
