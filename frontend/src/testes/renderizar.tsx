import { QueryClient } from '@tanstack/react-query';
import { render } from '@testing-library/react';
import { createMemoryRouter, RouterProvider } from 'react-router';

import { Provedores } from '../app/provedores';
import { rotas } from '../app/rotas';

/** Renderiza a aplicação inteira, com as rotas reais, a partir de um endereço. */
export function renderizarApp(caminho: string) {
  const roteador = createMemoryRouter(rotas, { initialEntries: [caminho] });
  // Sem tentativas repetidas: um erro da API aparece na hora, em vez de depois de 1 segundo.
  const cliente = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  const resultado = render(
    <Provedores cliente={cliente}>
      <RouterProvider router={roteador} />
    </Provedores>,
  );
  return { ...resultado, roteador, cliente };
}
