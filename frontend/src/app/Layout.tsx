import { Link, Outlet, useNavigate } from 'react-router';

import { Botao } from '../componentes/Botao';
import { useSair } from '../funcionalidades/contas/sessao';

/** Cabeçalho comum às telas de quem entrou: navegação principal e o botão Sair. */
export function Layout() {
  const sair = useSair();
  const navegar = useNavigate();

  return (
    <>
      <a
        href="#conteudo"
        className="sr-only focus:not-sr-only focus:absolute focus:left-2 focus:top-2 focus:bg-surface focus:p-2"
      >
        Pular para o conteúdo
      </a>
      <header className="flex flex-wrap items-center justify-between gap-3 bg-chrome px-4 py-3 text-on-chrome">
        <Link to="/" className="text-lg font-extrabold">
          Farol
        </Link>
        <nav aria-label="Principal" className="flex gap-4 font-bold">
          <Link to="/">Início</Link>
          <Link to="/disciplinas">Disciplinas</Link>
        </nav>
        <Botao
          variante="secundario"
          onClick={() => sair.mutate(undefined, { onSuccess: () => navegar('/entrar') })}
        >
          Sair
        </Botao>
      </header>
      <Outlet />
    </>
  );
}
