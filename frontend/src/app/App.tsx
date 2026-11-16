import { createBrowserRouter } from 'react-router';
import { RouterProvider } from 'react-router/dom';

import { Provedores } from './provedores';
import { rotas } from './rotas';

const roteador = createBrowserRouter(rotas);

export function App() {
  return (
    <Provedores>
      <RouterProvider router={roteador} />
    </Provedores>
  );
}
