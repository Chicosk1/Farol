import { Link } from 'react-router';

import { classesDoBotao } from '../../componentes/classes';
import { Icone } from '../../componentes/Icone';
import { useDisciplinas } from '../disciplinas/consultas';

/** O cartão do tutor na tela inicial, como no protótipo: o atalho para perguntar. */
export function CartaoDoTutor() {
  const comTutor = useDisciplinas('', 'com-tutor');
  const lista = comTutor.data ?? [];
  const disciplina = lista.find((d) => d.favorita) ?? lista[0];

  return (
    <section className="panel home-card" aria-labelledby="titulo-cartao-tutor">
      <div className="home-card-head">
        <span className="home-card-icon">
          <Icone nome="message-circle" />
        </span>
        <h2 id="titulo-cartao-tutor" className="card-heading">
          {disciplina ? `Tutor de ${disciplina.nome}` : 'Tutor'}
        </h2>
      </div>
      {disciplina ? (
        <>
          <p className="home-card-text">
            Ficou com dúvida da aula? Pergunte ao tutor: ele responde com o material do professor e
            mostra a página.
          </p>
          <Link
            className={classesDoBotao('contorno', true)}
            to={`/disciplinas/${disciplina.id}/tutor`}
          >
            Abrir tutor
          </Link>
        </>
      ) : (
        <p className="home-card-text">
          O tutor começa a responder quando o professor publicar os materiais da disciplina.
        </p>
      )}
    </section>
  );
}
