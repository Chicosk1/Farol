import type { RouteObject } from 'react-router';

import { ExigeLogin } from '../funcionalidades/contas/ExigeLogin';
import { PaginaEntrar } from '../funcionalidades/contas/PaginaEntrar';
import { PaginaMeusDados } from '../funcionalidades/contas/PaginaMeusDados';
import { PaginaDisciplinas } from '../funcionalidades/disciplinas/PaginaDisciplinas';
import { PaginaDuvidas } from '../funcionalidades/duvidas/PaginaDuvidas';
import { PaginaDaDisciplina } from '../funcionalidades/materiais/PaginaDaDisciplina';
import { PaginaMateriais } from '../funcionalidades/materiais/PaginaMateriais';
import { PaginaTrecho } from '../funcionalidades/materiais/PaginaTrecho';
import { PaginaQuestoes } from '../funcionalidades/questoes/PaginaQuestoes';
import { PaginaQuiz } from '../funcionalidades/questoes/PaginaQuiz';
import { PaginaRevisao } from '../funcionalidades/revisao/PaginaRevisao';
import { PaginaConfiguracaoDoTutor } from '../funcionalidades/tutor/PaginaConfiguracaoDoTutor';
import { PaginaTutor } from '../funcionalidades/tutor/PaginaTutor';
import { PaginaTutorInicial } from '../funcionalidades/tutor/PaginaTutorInicial';
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
          { path: '/meus-dados', element: <PaginaMeusDados /> },
          { path: '/revisao', element: <PaginaRevisao /> },
          { path: '/disciplinas/:id', element: <PaginaDaDisciplina /> },
          { path: '/disciplinas/:id/materiais', element: <PaginaMateriais /> },
          { path: '/disciplinas/:id/duvidas', element: <PaginaDuvidas /> },
          { path: '/disciplinas/:id/questoes', element: <PaginaQuestoes /> },
          { path: '/disciplinas/:id/quiz/:materialId', element: <PaginaQuiz /> },
          { path: '/trechos/:id', element: <PaginaTrecho /> },
          { path: '/tutor', element: <PaginaTutorInicial /> },
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
