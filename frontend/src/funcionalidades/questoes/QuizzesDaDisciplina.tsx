import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router';

import { listarQuizzes } from '../../api/cliente';
import { Icone } from '../../componentes/Icone';

/** Os quizzes da disciplina na página do aluno, com o andamento de cada um (QUE-RF-07). */
export function QuizzesDaDisciplina({ disciplinaId }: { disciplinaId: number }) {
  const quizzes = useQuery({
    queryKey: ['quizzes', disciplinaId],
    queryFn: () => listarQuizzes(disciplinaId),
  });

  if (quizzes.isPending) {
    return <p className="muted">Carregando os quizzes…</p>;
  }
  if (quizzes.isError || quizzes.data.length === 0) {
    return (
      <ul className="panel list">
        <li className="list-row muted">Nenhum quiz publicado ainda.</li>
      </ul>
    );
  }
  return (
    <ul className="panel list" aria-label="Quizzes">
      {quizzes.data.map((quiz) => {
        const concluido = quiz.respondidas >= quiz.questoes;
        const andamento = concluido
          ? `Concluído: ${quiz.acertos} de ${quiz.questoes} acertos`
          : quiz.respondidas
            ? `${quiz.respondidas} de ${quiz.questoes} respondidas`
            : `${quiz.questoes} ${quiz.questoes === 1 ? 'questão' : 'questões'}`;
        return (
          <li key={quiz.material}>
            <Link
              className="list-row list-row--action"
              to={`/disciplinas/${disciplinaId}/quiz/${quiz.material}`}
            >
              <span className="file-icon">
                <Icone nome={concluido ? 'circle-check' : 'list-check'} />
              </span>
              <span className="list-row-main">
                <span>
                  Quiz da Aula {quiz.aula_numero} · {quiz.aula_titulo}
                </span>
                <span className="small muted">{andamento}</span>
              </span>
              <Icone nome="chevron-right" />
            </Link>
          </li>
        );
      })}
    </ul>
  );
}
