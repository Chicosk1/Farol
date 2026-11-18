import type { ReactNode } from 'react';
import { Link } from 'react-router';

import type { Disciplina } from '../../api/cliente';
import { Icone } from '../../componentes/Icone';
import type { NomeDoIcone } from '../../componentes/icones';
import { Selo } from '../../componentes/Selo';
import { iconeDaDisciplina } from './icones';

type Props = {
  disciplina: Disciplina;
  /** Para onde o título leva: a página da disciplina do aluno ou os materiais do professor. */
  destino: string;
  /** Nível do título, para seguir a hierarquia da página. */
  nivel?: 2 | 3;
  /** Atalhos do rodapé do cartão, como o tutor. */
  atalhos?: ReactNode;
  favoritando?: boolean;
  aoFavoritar?: (favorita: boolean) => void;
};

/** O cartão de disciplina do protótipo (fr-card), com a estrela de favorita (ACE-RF-10). */
export function CartaoDeDisciplina({
  disciplina,
  destino,
  nivel = 2,
  atalhos,
  favoritando = false,
  aoFavoritar,
}: Props) {
  const Titulo = nivel === 2 ? 'h2' : 'h3';
  return (
    <article className="fr-card is-clickable">
      <div className="fr-card-media">
        <Icone nome={iconeDaDisciplina(disciplina.nome)} />
        {aoFavoritar && (
          <button
            type="button"
            className={disciplina.favorita ? 'fr-card-fav is-fav' : 'fr-card-fav'}
            aria-label={`Favoritar ${disciplina.nome}`}
            aria-pressed={disciplina.favorita}
            disabled={favoritando}
            onClick={() => aoFavoritar(!disciplina.favorita)}
          >
            <Icone nome="star" />
          </button>
        )}
        {disciplina.tem_tutor ? (
          <Selo tom="destaque" pilula icone="message-circle">
            Com tutor
          </Selo>
        ) : (
          <Selo icone="tag">Turma {disciplina.turma}</Selo>
        )}
      </div>
      <div className="fr-card-body">
        <Titulo className="fr-card-title">
          <Link className="card-link" to={destino}>
            {disciplina.nome} ({disciplina.codigo})
          </Link>
        </Titulo>
        <div className="fr-meta">
          <Icone nome="user" />
          Prof. {disciplina.professor_nome}
        </div>
        <div className="fr-card-dates">
          <span>Turma {disciplina.turma}</span>
          <span>Semestre {disciplina.semestre}</span>
        </div>
        {atalhos && <div className="fr-card-foot cartao-atalhos">{atalhos}</div>}
      </div>
    </article>
  );
}

/** A linha de disciplina do modo lista do protótipo (course-row). */
export function LinhaDeDisciplina({
  disciplina,
  destino,
}: {
  disciplina: Disciplina;
  destino: string;
}) {
  return (
    <Link className="course-row" to={destino}>
      <span className="course-row-icon">
        <Icone nome={iconeDaDisciplina(disciplina.nome)} />
      </span>
      <span className="course-row-main">
        <span className="strong">
          {disciplina.nome} ({disciplina.codigo})
        </span>
        <span className="small muted">
          Prof. {disciplina.professor_nome} · Turma {disciplina.turma}
        </span>
      </span>
      {disciplina.tem_tutor && (
        <Selo tom="destaque" pilula>
          Com tutor
        </Selo>
      )}
      <Icone nome="chevron-right" />
    </Link>
  );
}

function Atalho({ para, icone, rotulo }: { para: string; icone: NomeDoIcone; rotulo: string }) {
  return (
    <Link className="fr-icon-btn fr-icon-btn--sm" to={para} aria-label={rotulo}>
      <Icone nome={icone} />
    </Link>
  );
}

/** Atalhos do cartão: materiais e tutor para o aluno; materiais, dúvidas e configuração para o professor. */
export function AtalhosDaDisciplina({
  disciplina,
  professor,
}: {
  disciplina: Disciplina;
  professor: boolean;
}) {
  const base = `/disciplinas/${disciplina.id}`;
  return (
    <>
      {professor && (
        <>
          <Atalho
            para={`${base}/materiais`}
            icone="files"
            rotulo={`Materiais de ${disciplina.nome}`}
          />
          <Atalho
            para={`${base}/duvidas`}
            icone="message-question"
            rotulo={`Dúvidas de ${disciplina.nome}`}
          />
          <Atalho
            para={`${base}/tutor/configuracao`}
            icone="settings"
            rotulo={`Configurar o tutor de ${disciplina.nome}`}
          />
        </>
      )}
      {!professor && disciplina.tem_tutor && (
        <Atalho
          para={`${base}/tutor`}
          icone="message-circle"
          rotulo={`Tutor de ${disciplina.nome}`}
        />
      )}
    </>
  );
}
