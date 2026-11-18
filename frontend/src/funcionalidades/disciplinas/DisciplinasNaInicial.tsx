import { Link } from 'react-router';

import { EstadoVazio } from '../../componentes/EstadoVazio';
import { Icone } from '../../componentes/Icone';
import { useEu } from '../contas/sessao';
import { AtalhosDaDisciplina, CartaoDeDisciplina } from './CartaoDeDisciplina';
import { useDefinirFavorito, useDisciplinas } from './consultas';

const QUANTAS = 3;

/**
 * "Suas disciplinas" na tela inicial, como no protótipo: até três cartões, com as favoritas no
 * topo (ACE-RF-10, cenário 3 da História 2).
 */
export function DisciplinasNaInicial() {
  const disciplinas = useDisciplinas('');
  const favoritar = useDefinirFavorito();
  const professor = useEu().data?.perfil_ativo === 'professor';
  const ordenadas = [...(disciplinas.data ?? [])].sort(
    (a, b) => Number(b.favorita) - Number(a.favorita),
  );
  const semFavoritas = ordenadas.length > 0 && !ordenadas.some((d) => d.favorita);

  return (
    <section className="stack" aria-labelledby="titulo-suas-disciplinas">
      <div className="section-head">
        <h2 id="titulo-suas-disciplinas" className="section-title">
          Suas disciplinas
        </h2>
        <Link className="link-btn" to="/disciplinas">
          Ver todas as disciplinas
          <Icone nome="chevron-right" />
        </Link>
      </div>

      {disciplinas.isError && (
        <p role="alert" className="notice notice--danger">
          <Icone nome="alert-triangle" />
          Não foi possível carregar as suas disciplinas.
        </p>
      )}
      {disciplinas.data?.length === 0 && (
        <EstadoVazio
          icone="school"
          titulo="Nenhuma disciplina ainda"
          texto="Se você já está matriculado, fale com a secretaria do curso para conferir a matrícula."
        />
      )}
      {semFavoritas && (
        <p className="small muted">
          Marque as suas favoritas com a estrela: elas ficam aqui, no topo.
        </p>
      )}
      {ordenadas.length > 0 && (
        <ul aria-label="Suas disciplinas" className="grid-cards">
          {ordenadas.slice(0, QUANTAS).map((disciplina) => (
            <li key={disciplina.id}>
              <CartaoDeDisciplina
                disciplina={disciplina}
                destino={`/disciplinas/${disciplina.id}/materiais`}
                nivel={3}
                atalhos={<AtalhosDaDisciplina disciplina={disciplina} professor={professor} />}
                favoritando={favoritar.isPending}
                aoFavoritar={(favorita) => favoritar.mutate({ id: disciplina.id, favorita })}
              />
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
