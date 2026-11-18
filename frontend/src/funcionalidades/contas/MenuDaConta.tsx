import { Link, useNavigate } from 'react-router';

import type { Perfil } from '../../api/cliente';
import { usePopover } from '../../app/popover';
import { Avatar } from '../../componentes/Avatar';
import { Icone } from '../../componentes/Icone';
import { useEu, useSair, useTrocarPerfil } from './sessao';

const NOMES_DOS_PERFIS: Record<Perfil, string> = {
  aluno: 'Aluno',
  professor: 'Professor',
  coordenacao: 'Coordenação',
  admin: 'Administrador',
};

/** O avatar do cabeçalho e o menu da conta: perfil em uso (ACE-RF-03), Meus dados e Sair. */
export function MenuDaConta() {
  const eu = useEu();
  const sair = useSair();
  const trocarPerfil = useTrocarPerfil();
  const navegar = useNavigate();
  const { aberto, botao, area, alternar, fechar, aoTeclar } = usePopover();

  if (!eu.data) return null;
  const pessoa = eu.data;

  return (
    <div ref={area} onKeyDown={aoTeclar}>
      <button
        ref={botao}
        type="button"
        className="avatar-btn"
        aria-label={`Conta de ${pessoa.nome}`}
        aria-expanded={aberto}
        aria-controls="menu-da-conta"
        onClick={alternar}
      >
        <Avatar nome={pessoa.nome} />
      </button>
      {aberto && (
        <div
          id="menu-da-conta"
          className="popover popover--small"
          role="dialog"
          aria-label="Sua conta"
        >
          <div className="popover-account">
            <Avatar nome={pessoa.nome} grande />
            <div>
              <p className="strong">{pessoa.nome}</p>
              <p className="small muted">{pessoa.email}</p>
            </div>
          </div>
          {/* Quem tem mais de um perfil troca o perfil em uso sem sair (ACE-RF-03). */}
          {pessoa.perfis.length > 1 && (
            <div className="fr-field popover-campo">
              <label htmlFor="perfil-em-uso" className="fr-label">
                Perfil em uso
              </label>
              <span className="fr-select-wrap">
                <select
                  id="perfil-em-uso"
                  className="fr-select"
                  value={pessoa.perfil_ativo ?? ''}
                  disabled={trocarPerfil.isPending}
                  onChange={(evento) => {
                    trocarPerfil.mutate(evento.target.value as Perfil, {
                      onSuccess: () => {
                        fechar();
                        navegar('/');
                      },
                    });
                  }}
                >
                  {pessoa.perfis.map((perfil) => (
                    <option key={perfil} value={perfil}>
                      {NOMES_DOS_PERFIS[perfil]}
                    </option>
                  ))}
                </select>
              </span>
            </div>
          )}
          {pessoa.perfil_ativo === 'aluno' && (
            <Link to="/meus-dados" className="popover-action" onClick={fechar}>
              <Icone nome="shield-lock" />
              Meus dados
            </Link>
          )}
          <button
            type="button"
            className="popover-action"
            onClick={() => sair.mutate(undefined, { onSuccess: () => navegar('/entrar') })}
          >
            <Icone nome="logout" />
            Sair
          </button>
        </div>
      )}
    </div>
  );
}
