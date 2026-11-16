import type { RouteObject } from 'react-router';

import { PaginaInicial } from './PaginaInicial';
import { PaginaNaoEncontrada } from './PaginaNaoEncontrada';

/** Rotas da aplicação. As telas de cada funcionalidade entram aqui a partir de `src/funcionalidades/`. */
export const rotas: RouteObject[] = [
  { path: '/', element: <PaginaInicial /> },
  { path: '*', element: <PaginaNaoEncontrada /> },
];
