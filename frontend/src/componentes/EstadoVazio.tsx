import type { ReactNode } from 'react';

import { Icone } from './Icone';
import type { NomeDoIcone } from './icones';

type Props = {
  icone: NomeDoIcone;
  titulo: string;
  texto?: ReactNode;
  /** Botão ou link para sair do estado vazio. */
  acao?: ReactNode;
};

/** Tela ou painel sem conteúdo, com um ícone, o motivo e o que fazer (classe empty-state). */
export function EstadoVazio({ icone, titulo, texto, acao }: Props) {
  return (
    <div className="empty-state">
      <span className="empty-state-icon">
        <Icone nome={icone} />
      </span>
      <h2 className="section-title">{titulo}</h2>
      {texto && <p className="muted">{texto}</p>}
      {acao}
    </div>
  );
}
