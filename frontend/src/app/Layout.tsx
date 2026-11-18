import { Link, Outlet, useNavigate } from 'react-router';

import { Botao } from '../componentes/Botao';
import { AvisoDePrivacidade } from '../funcionalidades/contas/AvisoDePrivacidade';
import type { Perfil } from '../api/cliente';
import { useEu, useSair, useTrocarPerfil } from '../funcionalidades/contas/sessao';
import { SinoDeNotificacoes } from '../funcionalidades/notificacoes/SinoDeNotificacoes';

const NOMES_DOS_PERFIS: Record<Perfil, string> = {
  aluno: 'Aluno',
  professor: 'Professor',
  coordenacao: 'Coordenação',
  admin: 'Administrador',
};

/** Cabeçalho comum às telas de quem entrou: navegação, troca de perfil e o botão Sair. */
export function Layout() {
  const eu = useEu();
  const sair = useSair();
  const trocarPerfil = useTrocarPerfil();
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
            {eu.data?.perfil_ativo === 'aluno' && <Link to="/meus-dados">Meus dados</Link>}
          </nav>
          <div className="flex items-center gap-2">
            {/* Quem tem mais de um perfil troca o perfil em uso sem sair (ACE-RF-03). */}
            {eu.data && eu.data.perfis.length > 1 && (
              <label className="flex items-center gap-2 text-sm font-bold">
                Perfil em uso
                <select
                  className="min-h-12 rounded-lg border border-line-control bg-surface px-2 text-ink"
                  value={eu.data.perfil_ativo ?? ''}
                  disabled={trocarPerfil.isPending}
                  onChange={(evento) => {
                    trocarPerfil.mutate(evento.target.value as Perfil, {
                      onSuccess: () => navegar('/'),
                    });
                  }}
                >
                  {eu.data.perfis.map((perfil) => (
                    <option key={perfil} value={perfil}>
                      {NOMES_DOS_PERFIS[perfil]}
                    </option>
                  ))}
                </select>
              </label>
            )}
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
