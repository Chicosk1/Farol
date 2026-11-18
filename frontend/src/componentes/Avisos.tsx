import { useCallback, useEffect, useRef, useState, type ReactNode } from 'react';

import { ContextoDosAvisos } from './contextoDosAvisos';
import { Icone } from './Icone';
import type { NomeDoIcone } from './icones';

const DURACAO_EM_MS = 3200;
const NO_MAXIMO = 2; // avisos ao mesmo tempo, como no protótipo

type Aviso = { id: number; texto: string; icone: NomeDoIcone };

/** Guarda os avisos da tela e os mostra numa região anunciada por leitores de tela. */
export function ProvedorDeAvisos({ children }: { children: ReactNode }) {
  const [avisos, setAvisos] = useState<Aviso[]>([]);
  const proximo = useRef(0);
  const relogios = useRef<number[]>([]);

  useEffect(() => {
    const ativos = relogios.current;
    return () => ativos.forEach((relogio) => window.clearTimeout(relogio));
  }, []);

  const mostrar = useCallback((texto: string, icone: NomeDoIcone = 'circle-check') => {
    proximo.current += 1;
    const id = proximo.current;
    setAvisos((atuais) => [...atuais, { id, texto, icone }].slice(-NO_MAXIMO));
    relogios.current.push(
      window.setTimeout(
        () => setAvisos((atuais) => atuais.filter((aviso) => aviso.id !== id)),
        DURACAO_EM_MS,
      ),
    );
  }, []);

  return (
    <ContextoDosAvisos.Provider value={mostrar}>
      {children}
      <div className="toast-host" role="status" aria-live="polite">
        {avisos.map((aviso) => (
          <div key={aviso.id} className="toast">
            <Icone nome={aviso.icone} />
            <span>{aviso.texto}</span>
          </div>
        ))}
      </div>
    </ContextoDosAvisos.Provider>
  );
}
