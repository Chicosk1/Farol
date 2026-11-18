import { useEffect, useId, useRef, type KeyboardEvent, type ReactNode } from 'react';
import { createPortal } from 'react-dom';

import { Icone } from './Icone';

type Props = {
  titulo: string;
  subtitulo?: string;
  largo?: boolean;
  /** Sem esta função, o modal só fecha pelos botões do próprio conteúdo (sem "Fechar" nem Esc). */
  aoFechar?: () => void;
  children: ReactNode;
};

const FOCAVEIS =
  'button:not([disabled]), a[href], input:not([disabled]), select, textarea, [tabindex]:not([tabindex="-1"])';

/**
 * Janela por cima da página (classes modal do protótipo). Prende o foco dentro dela, fecha com Esc
 * e devolve o foco a quem a abriu (ACE-RNF-01).
 */
export function Modal({ titulo, subtitulo, largo = false, aoFechar, children }: Props) {
  const idDoTitulo = useId();
  const caixa = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const quemAbriu = document.activeElement as HTMLElement | null;
    const primeiro = caixa.current?.querySelector<HTMLElement>(FOCAVEIS);
    (primeiro ?? caixa.current)?.focus();
    return () => {
      if (quemAbriu && document.contains(quemAbriu)) quemAbriu.focus();
    };
  }, []);

  const aoTeclar = (evento: KeyboardEvent<HTMLDivElement>) => {
    if (evento.key === 'Escape' && aoFechar) {
      evento.stopPropagation();
      aoFechar();
      return;
    }
    if (evento.key !== 'Tab' || !caixa.current) return;
    const focaveis = [...caixa.current.querySelectorAll<HTMLElement>(FOCAVEIS)];
    const primeiro = focaveis[0];
    const ultimo = focaveis[focaveis.length - 1];
    if (evento.shiftKey && document.activeElement === primeiro) {
      evento.preventDefault();
      ultimo?.focus();
    } else if (!evento.shiftKey && document.activeElement === ultimo) {
      evento.preventDefault();
      primeiro?.focus();
    }
  };

  return createPortal(
    <div
      className="modal-backdrop"
      onClick={(evento) => {
        if (evento.target === evento.currentTarget) aoFechar?.();
      }}
    >
      <div
        ref={caixa}
        className={largo ? 'modal modal--wide' : 'modal'}
        role="dialog"
        aria-modal="true"
        aria-labelledby={idDoTitulo}
        tabIndex={-1}
        onKeyDown={aoTeclar}
      >
        <div className="modal-head">
          <div>
            <h2 id={idDoTitulo} className="modal-title">
              {titulo}
            </h2>
            {subtitulo && <p className="small muted">{subtitulo}</p>}
          </div>
          {aoFechar && (
            <button type="button" className="fr-icon-btn" aria-label="Fechar" onClick={aoFechar}>
              <Icone nome="x" />
            </button>
          )}
        </div>
        <div className="modal-body">{children}</div>
      </div>
    </div>,
    document.body,
  );
}
