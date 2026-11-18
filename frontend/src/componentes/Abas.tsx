import { useId, useRef, type KeyboardEvent, type ReactNode } from 'react';

type Aba<T extends string> = { id: T; rotulo: string };

type PropsDaLista<T extends string> = {
  /** Nome da lista de abas, lido por leitores de tela. */
  rotulo: string;
  abas: readonly Aba<T>[];
  ativa: T;
  aoMudar: (id: T) => void;
  /** O id do painel que as abas controlam. */
  idDoPainel: string;
  /** Prefixo dos ids das abas, para o painel apontar para a aba ativa. */
  base: string;
};

/**
 * Só a lista de abas (fr-tabs), para quando ela fica numa barra de ferramentas, longe do painel.
 * Padrão ARIA: só a aba ativa entra na ordem do Tab, e as setas, Home e End movem entre as abas.
 */
export function ListaDeAbas<T extends string>({
  rotulo,
  abas,
  ativa,
  aoMudar,
  idDoPainel,
  base,
}: PropsDaLista<T>) {
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
    <div role="tablist" aria-label={rotulo} className="fr-tabs">
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
            aria-controls={idDoPainel}
            tabIndex={selecionada ? 0 : -1}
            onClick={() => aoMudar(aba.id)}
            onKeyDown={(evento) => aoTeclar(evento, indice)}
            className="fr-tab"
          >
            {aba.rotulo}
          </button>
        );
      })}
    </div>
  );
}

type Props<T extends string> = Omit<PropsDaLista<T>, 'idDoPainel' | 'base'> & {
  /** Conteúdo do painel da aba ativa. */
  children: ReactNode;
};

/** Abas do design system com o painel logo abaixo: um único painel mostra a aba ativa. */
export function Abas<T extends string>({ children, ...lista }: Props<T>) {
  const base = useId();
  return (
    <div className="stack">
      <ListaDeAbas {...lista} base={base} idDoPainel={`${base}-painel`} />
      <div role="tabpanel" id={`${base}-painel`} aria-labelledby={`${base}-${lista.ativa}`}>
        {children}
      </div>
    </div>
  );
}
