import { useState } from 'react';
import { Link, Outlet, useLocation, useMatch } from 'react-router';

import { Icone } from '../componentes/Icone';
import type { NomeDoIcone } from '../componentes/icones';
import { AvisoDePrivacidade } from '../funcionalidades/contas/AvisoDePrivacidade';
import { MenuDaConta } from '../funcionalidades/contas/MenuDaConta';
import { useEu } from '../funcionalidades/contas/sessao';
import { useDisciplinas } from '../funcionalidades/disciplinas/consultas';
import { SinoDeNotificacoes } from '../funcionalidades/notificacoes/SinoDeNotificacoes';
import { useTelaEstreita } from './telaEstreita';

type Item = {
  rotulo: string;
  curto: string;
  icone: NomeDoIcone;
  para: string;
  /** Se o item é o da página atual. */
  atual: (caminho: string) => boolean;
};

const TUTOR = /^\/(?:tutor|disciplinas\/\d+\/tutor)$/;

/** O menu do aluno é o mesmo em todas as telas, como no protótipo. */
function itensDoAluno(): Item[] {
  return [
    { rotulo: 'Início', curto: 'Início', icone: 'home', para: '/', atual: (c) => c === '/' },
    {
      rotulo: 'Disciplinas',
      curto: 'Disciplinas',
      icone: 'school',
      para: '/disciplinas',
      atual: (c) => c.startsWith('/disciplinas') && !TUTOR.test(c),
    },
    {
      rotulo: 'Tutor',
      curto: 'Tutor',
      icone: 'message-circle',
      para: '/tutor',
      atual: (c) => TUTOR.test(c),
    },
  ];
}

/**
 * O professor trabalha numa turma de cada vez: dentro de uma disciplina, o menu mostra as telas
 * dela, como o menu do protótipo; fora, o início e a lista de disciplinas.
 */
function itensDoProfessor(disciplinaId: string | undefined): Item[] {
  if (!disciplinaId) {
    return [
      { rotulo: 'Início', curto: 'Início', icone: 'home', para: '/', atual: (c) => c === '/' },
      {
        rotulo: 'Disciplinas',
        curto: 'Disciplinas',
        icone: 'school',
        para: '/disciplinas',
        atual: (c) => c === '/disciplinas',
      },
    ];
  }
  const base = `/disciplinas/${disciplinaId}`;
  return [
    {
      rotulo: 'Materiais',
      curto: 'Materiais',
      icone: 'files',
      para: `${base}/materiais`,
      atual: (c) => c === `${base}/materiais`,
    },
    {
      rotulo: 'Questões',
      curto: 'Questões',
      icone: 'list-check',
      para: `${base}/questoes`,
      atual: (c) => c === `${base}/questoes`,
    },
    {
      rotulo: 'Dúvidas',
      curto: 'Dúvidas',
      icone: 'message-question',
      para: `${base}/duvidas`,
      atual: (c) => c === `${base}/duvidas`,
    },
    {
      rotulo: 'Disciplina',
      curto: 'Disciplina',
      icone: 'settings',
      para: `${base}/tutor/configuracao`,
      atual: (c) => c === `${base}/tutor/configuracao`,
    },
    {
      rotulo: 'Todas as disciplinas',
      curto: 'Todas',
      icone: 'school',
      para: '/',
      atual: () => false,
    },
  ];
}

function FaixaDoProfessor({ disciplinaId }: { disciplinaId: string }) {
  const disciplinas = useDisciplinas('');
  const disciplina = disciplinas.data?.find((d) => String(d.id) === disciplinaId);
  return (
    <div className="sidebar-context">
      <span className="small">Turma</span>
      <b>{disciplina ? `${disciplina.nome} · ${disciplina.turma}` : 'Disciplina'}</b>
    </div>
  );
}

/**
 * A moldura das telas de quem entrou, igual à do protótipo: cabeçalho com a marca, o sino e a
 * conta; menu lateral no computador e barra inferior no celular.
 */
export function Layout() {
  const eu = useEu();
  const caminho = useLocation().pathname;
  const naDisciplina = useMatch('/disciplinas/:id/*');
  const telaEstreita = useTelaEstreita();
  const [recolhido, setRecolhido] = useState(false);
  const precisaVerAviso = eu.data?.precisa_ver_aviso === true;
  const professor = eu.data?.perfil_ativo === 'professor';
  const disciplinaId = professor ? naDisciplina?.params.id : undefined;
  const itens = professor ? itensDoProfessor(disciplinaId) : itensDoAluno();

  const links = (item: Item, curto: boolean) => (
    <Link
      key={item.para + item.rotulo}
      to={item.para}
      className={curto ? undefined : 'fr-nav-item'}
      aria-current={item.atual(caminho) ? 'page' : undefined}
    >
      <Icone nome={item.icone} />
      {curto ? <span>{item.curto}</span> : item.rotulo}
    </Link>
  );

  return (
    <>
      {/* Com o aviso de privacidade aberto, o resto da página não recebe foco nem cliques. */}
      <div className="app" data-menu={recolhido ? 'recolhido' : undefined} inert={precisaVerAviso}>
        <a href="#conteudo" className="skip-link">
          Pular para o conteúdo
        </a>
        <header className="fr-header">
          <button
            type="button"
            className="fr-icon-btn hide-mobile"
            aria-label={recolhido ? 'Abrir menu' : 'Recolher menu'}
            aria-expanded={!recolhido}
            onClick={() => setRecolhido((valor) => !valor)}
          >
            <Icone nome="menu-2" />
          </button>
          <Link to="/" className="fr-wordmark brand-link" aria-label="Farol, página inicial">
            <b>Farol</b>
            <span>{professor ? 'Painel do professor' : 'Tutor de estudos'}</span>
          </Link>
          <div className="fr-header-spacer" />
          <SinoDeNotificacoes />
          <MenuDaConta />
        </header>
        {!telaEstreita && (
          <nav className="fr-sidebar" aria-label="Menu principal">
            <div className="fr-sidebar-band">
              {disciplinaId ? (
                <FaixaDoProfessor disciplinaId={disciplinaId} />
              ) : (
                <Link className="fr-sidebar-search" to="/disciplinas">
                  <Icone nome="search" />
                  Buscar disciplina
                </Link>
              )}
            </div>
            <div className="fr-nav">{itens.map((item) => links(item, false))}</div>
          </nav>
        )}
        <main className="app-main" id="conteudo">
          <Outlet />
        </main>
        {telaEstreita && (
          <nav className="tabbar" aria-label="Menu principal">
            {itens.map((item) => links(item, true))}
          </nav>
        )}
      </div>
      {precisaVerAviso && <AvisoDePrivacidade />}
    </>
  );
}
