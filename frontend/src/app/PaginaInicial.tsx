import { useEu } from '../funcionalidades/contas/sessao';
import { DisciplinasNaInicial } from '../funcionalidades/disciplinas/DisciplinasNaInicial';
import { TurmasDoProfessor } from '../funcionalidades/disciplinas/TurmasDoProfessor';
import { Novidades } from '../funcionalidades/notificacoes/Novidades';
import { CartaoDoTutor } from '../funcionalidades/tutor/CartaoDoTutor';
import { hojePorExtenso } from './datas';

/**
 * Tela inicial, como no protótipo. O aluno vê os atalhos de estudo, as novidades e as disciplinas,
 * com as favoritas no topo; o professor vê as novidades e as turmas que leciona.
 */
export function PaginaInicial() {
  const eu = useEu();
  const primeiroNome = eu.data?.nome.split(' ')[0] ?? '';
  const professor = eu.data?.perfil_ativo === 'professor';

  return (
    <div className="page">
      <div className="page-head">
        <div>
          <h1 className="page-title">Olá, {primeiroNome}</h1>
          <p className="page-sub">{hojePorExtenso()}</p>
        </div>
      </div>
      {professor ? (
        <>
          <Novidades />
          <TurmasDoProfessor />
        </>
      ) : (
        <>
          <div className="home-grid">
            <CartaoDoTutor />
          </div>
          <Novidades />
          <DisciplinasNaInicial />
        </>
      )}
    </div>
  );
}
