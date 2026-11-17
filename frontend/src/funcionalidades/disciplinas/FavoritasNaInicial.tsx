import { Link } from 'react-router';

import { useDisciplinas } from './consultas';

/** As disciplinas favoritas da pessoa, para o topo da tela inicial (ACE-RF-10). */
export function FavoritasNaInicial() {
  const favoritas = useDisciplinas('', 'favoritas');

  return (
    <section aria-labelledby="titulo-favoritas" className="mt-6">
      <h2 id="titulo-favoritas" className="text-base font-bold text-ink">
        Suas disciplinas favoritas
      </h2>

      {favoritas.isError && (
        <p role="alert" className="mt-2 text-danger-text">
          Não foi possível carregar as disciplinas favoritas.
        </p>
      )}
      {favoritas.data && favoritas.data.length > 0 && (
        <ul aria-label="Disciplinas favoritas" className="mt-2 grid gap-3 sm:grid-cols-2">
          {favoritas.data.map((disciplina) => (
            <li
              key={disciplina.id}
              className="rounded-lg border border-line bg-surface p-4 text-ink"
            >
              <p className="font-bold">{disciplina.nome}</p>
              <p className="text-sm text-ink-muted">
                {disciplina.codigo} · {disciplina.turma}
              </p>
              <p className="text-sm text-ink-muted">Prof. {disciplina.professor_nome}</p>
            </li>
          ))}
        </ul>
      )}
      {favoritas.data?.length === 0 && (
        <p className="mt-2 text-ink-muted">
          Você ainda não marcou favoritas. Use a estrela, na tela de disciplinas, para ter as suas
          aqui.
        </p>
      )}
      <Link to="/disciplinas" className="mt-3 inline-block font-bold text-accent underline">
        Ver todas as disciplinas
      </Link>
    </section>
  );
}
