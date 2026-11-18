import { createContext, useContext } from 'react';

import type { NomeDoIcone } from './icones';

export type MostrarAviso = (texto: string, icone?: NomeDoIcone) => void;

export const ContextoDosAvisos = createContext<MostrarAviso>(() => {});

/** Mostra um aviso curto no rodapé da tela, que some sozinho (toast do protótipo). */
export function useAvisos(): MostrarAviso {
  return useContext(ContextoDosAvisos);
}
