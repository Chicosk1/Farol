import { useId, useRef, type KeyboardEvent, type ReactNode } from 'react';

type Aba<T extends string> = { id: T; rotulo: string };

type Props<T extends string> = {
  /** Nome da lista de abas, lido por leitores de tela. */
  rotulo: string;
  abas: readonly Aba<T>[];
  ativa: T;
  aoMudar: (id: T) => void;
  /** Conteúdo do painel da aba ativa. */
  children: ReactNode;
};

/**
 * Abas do design system Farol, no padrão ARIA: só a aba ativa entra na ordem do Tab, e as setas,
 * Home e End movem entre as abas. Um único painel mostra o conteúdo da aba ativa.
 */
export function Abas<T extends string>({ rotulo, abas, ativa, aoMudar, children }: Props<T>) {
  const base = useId();
  const botoes = useRef(new Map<T, HTMLButtonElement>());

  const ir = (indice: number) => {
    const destino = abas[(indice + abas.length) % abas.length];
    if (destino) {
      aoMudar(destino.id);
      botoes.current.get(destino.id)?.focus();
    }
  };

  const aoTeclar = (evento: KeyboardEvent, indice: number) => {
    const movimentos: Record<string, number | undefined> = {
      ArrowRight: indice + 1,
      ArrowLeft: indice - 1,
      Home: 0,
      End: abas.length - 1,
    };
    const destino = movimentos[evento.key];
    if (destino !== undefined) {
      evento.preventDefault();
      ir(destino);
    }
  };

  return (
    <div>
      <div role="tablist" aria-label={rotulo} className="flex gap-1 border-b border-line">
        {abas.map((aba, indice) => {
          const selecionada = aba.id === ativa;
          return (
            <button
              key={aba.id}
              id={`${base}-${aba.id}`}
              ref={(elemento) => {
                if (elemento) botoes.current.set(aba.id, elemento);
              }}
              type="button"
              role="tab"
              aria-selected={selecionada}
              aria-controls={`${base}-painel`}
              tabIndex={selecionada ? 0 : -1}
              onClick={() => aoMudar(aba.id)}
              onKeyDown={(evento) => aoTeclar(evento, indice)}
              className={
                'min-h-12 px-4 font-bold ' +
                (selecionada
                  ? 'border-b-4 border-accent text-accent'
                  : 'border-b-4 border-transparent text-ink-muted')
              }
            >
              {aba.rotulo}
            </button>
          );
        })}
      </div>
      <div role="tabpanel" id={`${base}-painel`} aria-labelledby={`${base}-${ativa}`}>
        {children}
      </div>
    </div>
  );
}
