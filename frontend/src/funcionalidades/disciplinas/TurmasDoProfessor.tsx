import { EstadoVazio } from '../../componentes/EstadoVazio';
import { Icone } from '../../componentes/Icone';
import { AtalhosDaDisciplina, CartaoDeDisciplina } from './CartaoDeDisciplina';
import { useDisciplinas } from './consultas';

/** As turmas do professor na tela inicial, com os atalhos de cada uma (ACE-RF-04). */
export function TurmasDoProfessor() {
  const disciplinas = useDisciplinas('');

  return (
    <section className="stack" aria-labelledby="titulo-suas-turmas">
      <h2 id="titulo-suas-turmas" className="section-title">
        Suas turmas
      </h2>
      {disciplinas.isError && (
        <p role="alert" className="notice notice--danger">
          <Icone nome="alert-triangle" />
          Não foi possível carregar as suas turmas.
        </p>
      )}
      {disciplinas.data?.length === 0 && (
        <EstadoVazio
          icone="school"
          titulo="Nenhuma turma ainda"
          texto="As turmas chegam pela importação do sistema acadêmico. Se faltar alguma, fale com a coordenação."
        />
      )}
      {disciplinas.data && disciplinas.data.length > 0 && (
        <ul aria-label="Suas turmas" className="grid-cards">
          {disciplinas.data.map((disciplina) => (
            <li key={disciplina.id}>
              <CartaoDeDisciplina
                disciplina={disciplina}
                destino={`/disciplinas/${disciplina.id}/materiais`}
                nivel={3}
                atalhos={<AtalhosDaDisciplina disciplina={disciplina} professor />}
              />
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
