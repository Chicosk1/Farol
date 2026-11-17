import { Link, Outlet, useNavigate } from 'react-router';

import { Botao } from '../componentes/Botao';
import { AvisoDePrivacidade } from '../funcionalidades/contas/AvisoDePrivacidade';
import { useEu, useSair } from '../funcionalidades/contas/sessao';
import { SinoDeNotificacoes } from '../funcionalidades/notificacoes/SinoDeNotificacoes';

/** Cabeçalho comum às telas de quem entrou: navegação principal e o botão Sair. */
export function Layout() {
  const eu = useEu();
  const sair = useSair();
  const navegar = useNavigate();
  const precisaVerAviso = eu.data?.precisa_ver_aviso === true;

  return (
    <>
      {/* Com o aviso de privacidade aberto, o resto da página não recebe foco nem cliques. */}
      <div inert={precisaVerAviso}>
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
          <div className="flex items-center gap-2">
            <SinoDeNotificacoes />
            <Botao
              variante="secundario"
              onClick={() => sair.mutate(undefined, { onSuccess: () => navegar('/entrar') })}
            >
              Sair
            </Botao>
          </div>
        </header>
        <Outlet />
      </div>
      {precisaVerAviso && <AvisoDePrivacidade />}
    </>
  );
}
