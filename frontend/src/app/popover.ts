import { useEffect, useRef, useState } from 'react';

/**
 * Estado de um menu suspenso do cabeçalho (popover do protótipo): abre e fecha pelo botão, fecha
 * com Esc ou com um clique fora, e devolve o foco ao botão quando fecha pelo teclado.
 */
export function usePopover<B extends HTMLElement = HTMLButtonElement>() {
  const [aberto, setAberto] = useState(false);
  const botao = useRef<B>(null);
  const area = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!aberto) return;
    const aoClicar = (evento: MouseEvent) => {
      if (area.current && !area.current.contains(evento.target as Node)) setAberto(false);
    };
    document.addEventListener('mousedown', aoClicar);
    return () => document.removeEventListener('mousedown', aoClicar);
  }, [aberto]);

  return {
    aberto,
    botao,
    area,
    alternar: () => setAberto((valor) => !valor),
    fechar: () => setAberto(false),
    /** Para o onKeyDown da área: Esc fecha e devolve o foco ao botão. */
    aoTeclar: (evento: { key: string }) => {
      if (evento.key === 'Escape' && aberto) {
        setAberto(false);
        botao.current?.focus();
      }
    },
  };
}
