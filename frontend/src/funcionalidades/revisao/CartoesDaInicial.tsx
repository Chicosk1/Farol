import { Link } from 'react-router';

import { classesDoBotao } from '../../componentes/classes';
import { Icone } from '../../componentes/Icone';
import { Progresso } from '../../componentes/Progresso';
import { useRevisaoDeHoje } from './consultas';

const INICIAIS = ['D', 'S', 'T', 'Q', 'Q', 'S', 'S'];

function diaDaSemana(data: string): number {
  const [ano, mes, dia] = data.split('-').map(Number);
  return new Date(ano!, mes! - 1, dia!).getDay();
}

/** O cartão "Revisão do dia" da tela inicial (REV-RF-06). */
export function CartaoDaRevisao() {
  const revisao = useRevisaoDeHoje();
  const dados = revisao.data;
  const total = dados?.cartoes.length ?? 0;
  const avaliadas = dados?.respostas.filter((r) => r.avaliacao).length ?? 0;
  let corpo;
  if (!dados) {
    corpo = <p className="home-card-text muted">Carregando…</p>;
  } else if (total === 0) {
    corpo = (
      <p className="home-card-text">
        {dados.tem_questoes
          ? 'Nada para revisar hoje. A próxima revisão fica pronta amanhã às 6h.'
          : 'A revisão começa quando os professores publicarem questões das aulas.'}
      </p>
    );
  } else if (dados.concluida) {
    const acertos = dados.respostas.filter((r) => r.acerto).length;
    corpo = (
      <>
        <p className="home-card-text">
          Concluída: {acertos} de {total} acertos. A próxima fica pronta amanhã às 6h.
        </p>
        <Link className={classesDoBotao('contorno', true)} to="/revisao">
          Ver resultado
        </Link>
      </>
    );
  } else {
    corpo = (
      <>
        <p className="home-card-text">
          {total} {total === 1 ? 'cartão' : 'cartões'} de {dados.disciplinas.join(' e ')}, cerca de{' '}
          {dados.minutos} {dados.minutos === 1 ? 'minuto' : 'minutos'}.
        </p>
        {avaliadas > 0 && (
          <Progresso valor={avaliadas} maximo={total} rotulo={`${avaliadas} de ${total} cartões`} />
        )}
        <Link className={classesDoBotao('primario', true)} to="/revisao">
          {avaliadas > 0 ? 'Continuar' : 'Começar revisão'}
        </Link>
      </>
    );
  }
  return (
    <section className="panel home-card home-card--review" aria-labelledby="titulo-revisao">
      <div className="home-card-head">
        <span className="home-card-icon">
          <Icone nome="cards" />
        </span>
        <h2 id="titulo-revisao" className="card-heading">
          Revisão do dia
        </h2>
      </div>
      {corpo}
    </section>
  );
}

/** O cartão da sequência dos últimos 7 dias (REV-RF-07). */
export function CartaoDaSequencia() {
  const dados = useRevisaoDeHoje().data;
  if (!dados) return null;
  const feitas = dados.sequencia.filter((d) => d.feita).length;
  const hojeFeita = dados.sequencia.at(-1)?.feita ?? false;
  const n = dados.dias_seguidos;
  const titulo = n === 0 ? 'Sequência' : n === 1 ? '1 dia seguido' : `${n} dias seguidos`;
  return (
    <section className="panel home-card" aria-labelledby="titulo-sequencia">
      <div className="home-card-head">
        <span className="home-card-icon home-card-icon--highlight">
          <Icone nome="flame" />
        </span>
        <h2 id="titulo-sequencia" className="card-heading">
          {titulo}
        </h2>
      </div>
      <p className="home-card-text">
        {hojeFeita
          ? 'Revisão de hoje feita. Volte amanhã para manter a sequência.'
          : 'Faça a revisão de hoje para manter a sequência.'}
      </p>
      <div
        className="streak"
        role="img"
        aria-label={`Revisão feita em ${feitas} dos últimos 7 dias`}
      >
        {dados.sequencia.map((dia, i) => (
          <span
            key={dia.data}
            className={[
              'streak-day',
              dia.feita ? 'is-done' : '',
              i === dados.sequencia.length - 1 ? 'is-today' : '',
            ]
              .filter(Boolean)
              .join(' ')}
            aria-hidden="true"
          >
            {INICIAIS[diaDaSemana(dia.data)]}
          </span>
        ))}
      </div>
    </section>
  );
}
