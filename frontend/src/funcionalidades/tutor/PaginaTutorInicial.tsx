import { Link, Navigate } from 'react-router';

import { classesDoBotao } from '../../componentes/classes';
import { EstadoVazio } from '../../componentes/EstadoVazio';
import { useDisciplinas } from '../disciplinas/consultas';

/**
 * O item "Tutor" do menu: abre o tutor da primeira disciplina com material pronto, favoritas
 * primeiro. Sem nenhuma, explica quando o tutor começa a funcionar.
 */
export function PaginaTutorInicial() {
  const comTutor = useDisciplinas('', 'com-tutor');

  if (comTutor.isPending) {
    return (
      <div className="page">
        <p role="status" className="muted">
          Carregando…
        </p>
      </div>
    );
  }
  const lista = comTutor.data ?? [];
  const primeira = lista.find((d) => d.favorita) ?? lista[0];
  if (primeira) return <Navigate to={`/disciplinas/${primeira.id}/tutor`} replace />;

  return (
    <div className="page">
      <h1 className="sr-only">Tutor</h1>
      <EstadoVazio
        icone="message-circle"
        titulo="Nenhum tutor disponível ainda"
        texto="O tutor funciona nas disciplinas em que o professor já publicou materiais."
        acao={
          <Link className={classesDoBotao('contorno')} to="/disciplinas">
            Ver disciplinas
          </Link>
        }
      />
    </div>
  );
}
