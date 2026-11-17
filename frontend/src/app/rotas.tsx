import type { RouteObject } from 'react-router';

import { ExigeLogin } from '../funcionalidades/contas/ExigeLogin';
import { PaginaEntrar } from '../funcionalidades/contas/PaginaEntrar';
import { PaginaDisciplinas } from '../funcionalidades/disciplinas/PaginaDisciplinas';
import { PaginaDuvidas } from '../funcionalidades/duvidas/PaginaDuvidas';
import { PaginaMateriais } from '../funcionalidades/materiais/PaginaMateriais';
import { PaginaConfiguracaoDoTutor } from '../funcionalidades/tutor/PaginaConfiguracaoDoTutor';
import { PaginaTutor } from '../funcionalidades/tutor/PaginaTutor';
import { Layout } from './Layout';
import { PaginaInicial } from './PaginaInicial';
import { PaginaNaoEncontrada } from './PaginaNaoEncontrada';

/** Rotas da aplicação. As telas de cada funcionalidade entram aqui a partir de `src/funcionalidades/`. */
export const rotas: RouteObject[] = [
  { path: '/entrar', element: <PaginaEntrar /> },
  {
    element: <ExigeLogin />,
    children: [
      {
        element: <Layout />,
        children: [
          { path: '/', element: <PaginaInicial /> },
          { path: '/disciplinas', element: <PaginaDisciplinas /> },
          { path: '/disciplinas/:id/materiais', element: <PaginaMateriais /> },
          { path: '/disciplinas/:id/duvidas', element: <PaginaDuvidas /> },
          { path: '/disciplinas/:id/tutor', element: <PaginaTutor /> },
          {
            path: '/disciplinas/:id/tutor/configuracao',
            element: <PaginaConfiguracaoDoTutor />,
          },
        ],
      },
    ],
  },
  { path: '*', element: <PaginaNaoEncontrada /> },
];
