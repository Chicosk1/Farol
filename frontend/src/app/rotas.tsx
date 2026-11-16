import type { RouteObject } from 'react-router';

import { ExigeLogin } from '../funcionalidades/contas/ExigeLogin';
import { PaginaEntrar } from '../funcionalidades/contas/PaginaEntrar';
import { PaginaInicial } from './PaginaInicial';
import { PaginaNaoEncontrada } from './PaginaNaoEncontrada';

/** Rotas da aplicação. As telas de cada funcionalidade entram aqui a partir de `src/funcionalidades/`. */
export const rotas: RouteObject[] = [
  { path: '/entrar', element: <PaginaEntrar /> },
  {
    element: <ExigeLogin />,
    children: [{ path: '/', element: <PaginaInicial /> }],
  },
  { path: '*', element: <PaginaNaoEncontrada /> },
];
