import { Navigate, Outlet } from 'react-router';

import { useEu } from './sessao';

/** Rotas filhas só para quem entrou; os demais vão para a tela de entrada. */
export function ExigeLogin() {
  const eu = useEu();

  if (eu.isPending) {
    return (
      <p role="status" className="p-4 text-ink-muted">
        Carregando…
      </p>
    );
  }
  if (!eu.data) {
    return <Navigate to="/entrar" replace />;
  }
  return <Outlet />;
}
