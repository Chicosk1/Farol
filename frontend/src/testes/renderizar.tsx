import { render } from '@testing-library/react';
import { createMemoryRouter, RouterProvider } from 'react-router';

import { Provedores } from '../app/provedores';
import { rotas } from '../app/rotas';

/** Renderiza a aplicação inteira, com as rotas reais, a partir de um endereço. */
export function renderizarApp(caminho: string) {
  const roteador = createMemoryRouter(rotas, { initialEntries: [caminho] });
  const resultado = render(
    <Provedores>
      <RouterProvider router={roteador} />
    </Provedores>,
  );
  return { ...resultado, roteador };
}
