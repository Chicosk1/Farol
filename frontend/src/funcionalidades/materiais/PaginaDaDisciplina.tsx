import { Link, useParams } from 'react-router';

import { classesDoBotao } from '../../componentes/classes';
import { EstadoVazio } from '../../componentes/EstadoVazio';
import { Icone } from '../../componentes/Icone';
import { useDisciplina } from '../disciplinas/consultas';
import { iconeDaDisciplina } from '../disciplinas/icones';
import { QuizzesDaDisciplina } from '../questoes/QuizzesDaDisciplina';
import { MateriaisDoAluno } from './MateriaisDoAluno';

/**
 * A página de uma disciplina para o aluno, como no protótipo: o cabeçalho com o acesso ao tutor,
 * os materiais prontos e os quizzes (MAT-RF-07, MAT-RF-08).
 */
export function PaginaDaDisciplina() {
  const id = Number(useParams().id);
  const disciplina = useDisciplina(id);

  if (disciplina.isError) {
    return (
      <div className="page">
        <h1 className="sr-only">Disciplina</h1>
        <EstadoVazio
          icone="school"
          titulo="Disciplina não encontrada"
          texto="Volte para a lista de disciplinas."
          acao={
            <Link className={classesDoBotao('contorno')} to="/disciplinas">
              Ver disciplinas
            </Link>
          }
        />
      </div>
    );
  }
  const dados = disciplina.data;

  return (
    <div className="page">
      <nav className="breadcrumb" aria-label="Você está em">
        <Link to="/disciplinas">Disciplinas</Link>
        <Icone nome="chevron-right" />
        <span aria-current="page">{dados?.nome ?? 'Disciplina'}</span>
      </nav>

      <div className="discipline-head panel">
        <span className="discipline-icon">
          <Icone nome={iconeDaDisciplina(dados?.nome ?? '')} />
        </span>
        <div className="discipline-info">
          <h1 className="page-title">
            {dados ? `${dados.nome} (${dados.codigo})` : 'Carregando a disciplina…'}
          </h1>
          {dados && (
            <p className="page-sub">
              Prof. {dados.professor_nome} · Turma {dados.turma} · {dados.semestre}
            </p>
          )}
        </div>
        <div className="discipline-actions">
          {dados?.tem_tutor ? (
            <Link className={classesDoBotao('primario')} to={`/disciplinas/${id}/tutor`}>
              <Icone nome="message-circle" />
              Perguntar ao tutor
            </Link>
          ) : (
            dados && (
              <p className="notice">
                <Icone nome="info-circle" />O tutor desta disciplina começa a funcionar quando o
                professor publicar os materiais.
              </p>
            )
          )}
        </div>
      </div>

      <div className="cols-2">
        <section className="stack" aria-labelledby="titulo-materiais">
          <h2 id="titulo-materiais" className="section-title">
            Materiais
          </h2>
          <MateriaisDoAluno disciplinaId={id} />
        </section>
        <section className="stack" aria-labelledby="titulo-quizzes">
          <h2 id="titulo-quizzes" className="section-title">
            Quizzes
          </h2>
          <QuizzesDaDisciplina disciplinaId={id} />
        </section>
      </div>
    </div>
  );
}
