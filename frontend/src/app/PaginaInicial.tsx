import { useEu } from '../funcionalidades/contas/sessao';
import { DisciplinasNaInicial } from '../funcionalidades/disciplinas/DisciplinasNaInicial';
import { Novidades } from '../funcionalidades/notificacoes/Novidades';
import { CartaoDoTutor } from '../funcionalidades/tutor/CartaoDoTutor';
import { hojePorExtenso } from './datas';

/**
 * Tela inicial do aluno, como no protótipo: a saudação com a data, os atalhos de estudo, as
 * novidades e as disciplinas, com as favoritas no topo.
 */
export function PaginaInicial() {
  const eu = useEu();
  const primeiroNome = eu.data?.nome.split(' ')[0] ?? '';

  return (
    <div className="page">
      <div className="page-head">
        <div>
          <h1 className="page-title">Olá, {primeiroNome}</h1>
          <p className="page-sub">{hojePorExtenso()}</p>
        </div>
      </div>
      <div className="home-grid">
        <CartaoDoTutor />
      </div>
      <Novidades />
      <DisciplinasNaInicial />
    </div>
  );
}
